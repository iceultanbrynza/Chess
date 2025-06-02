from channels.generic.websocket import AsyncJsonWebsocketConsumer, JsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Game
from django.contrib.auth.models import User
from engine import logic

# GameConsumer
# We assign id to game using HTTP request without any socket.
# Create Connection between user and server based on game id.

# Verify that the game with given id do exists, otherwise cancel the connection.
# cancellation - self.close()

# If the game exists, we create a room that contains two players
# (self.channel_layer.group_add(desired id of room, channel_name)).
# Room is aimed to make
# broadcast (self.channel_layer.group_send(id of room, data including both type and event))

# If game do exists, return the information about side color, if the opponent is online,
# pgn to particular user who connected to this websocket (because we use send_json method
# - which works analogously to serializer in REST). This command is called by one user and message
# is sent to another user

# if opponent turned off, it considered as resignment

class GameConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
            return
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        data =  await self.verify(self.game_id)
        if not data:
            await self.close()
        await self.accept()
        await self.join_room(data)
        if data[2]:
            await self.declare_online()

    async def receive_json(self, content):
        command = content['command']
        if command == 'make_move':
            await self.make_move()
        if command == 'resign':
            await self.declare_resignment()

    async def make_move(self, id, pos1, pos2, fen):
        board = logic.create_board(fen)
        data = logic.make_move(board, pos1, pos2)
        pgn = logic.board_to_pgn()
        if data['checkmate']:
            await self.channel_layer.group_send(
                str(self.game_id),
                {
                    "type": "declare.move",
                    'sender_channel_name': self.channel_name,
                    "message": {
                        "user": id,
                        "source": pos1,
                        "target": pos2,
                        "pgn": pgn,
                        "fen": data['fen'],
                        "check": data['check'],
                        "checkmate": True
                    }
                }
            )
        else:
            await self.channel_layer.group_send({
                str(self.game_id),
                {
                    "type": "declare.move",
                    'sender_channel_name': self.channel_name,
                    "message": {
                        "user": id,
                        "source": pos1,
                        "target": pos2,
                        "pgn": pgn,
                        "fen": data['fen'],
                        "check": data['check'],
                        "checkmate": False
                    }
                }
            })

    async def declare_move(self, event):
        if self.channel_name == event['sender_channel_name']:
            await self.update(event['message']['fen'], event['message']['pgn'], event['message']['checkmate'])

        await self.send_json({
            "message": event['message']
        })
# "source": event['source'],
# "target": event['target'],
# "pgn": event['pgn'],
# "fen": event['fen']
    async def disconnect(self):
        if hasattr(self, "game_id"):
            await self.game_over()
        await self.declare_offline()

    async def join_room(self, data):
        await self.channel_layer.group_add(
            str(self.game_id),
            self.channel_name
        )
        await self.send_json(
            {
                "command": "join",
                "side": data[0],
                "fen": data[1],
                "opponent": data[2],
            }
        )

    async def declare_online(self):
        # function to declare that room is full.
        # the message is designated to the Owner of the Game
        await self.channel_layer.group_send(
            str(self.game_id),
            {
                "type": "declare",
                'sender_channel_name': self.channel_name,
                "message": "opponent joined the room"
            }
        )

    async def declare_offline(self):
        # function to declare that room is full.
        # the message is designated to the Owner of the Game
        # the message has to be handled on frontend side and corresponding
        # result should be presented to the winner
        await self.channel_layer.group_send(
            str(self.game_id),
            {
                "type": "declare",
                'sender_channel_name': self.channel_name,
                "message": "opponent left the room"
            }
        )

    async def declare_resignment(self):
        await self.channel_layer.group_send(
            str(self.game_id),
            {
                "type": "declare",
                'sender_channel_name': self.channel_name,
                "message": "opponent resigned"
            }
        )
        await self.game_over()

    async def declare(self, event):
        if event['sender_channel_name'] != self.channel_name:
            await self.send_json(
                {
                    "command": event['message']
                }
            )

    @database_sync_to_async
    def verify(self, game_id):
        game = Game.objects.filter(id=game_id).first()
        if game is None:
            return False

        user = self.scope['user']
        opp = False
        side = 'black'
        if game.owner == user:
            if game.owner_side == 'white':
                side = 'white'
            if game.opponent_online == True:
                opp = True

        elif game.opponent == user:
            if game.owner_side == 'black':
                side = 'white'
            if game.owner_online == True:
                opp = True

        else:
            return False

        return [side, game.fen, opp]

    @database_sync_to_async
    def game_over(self):
        user = self.scope['user']
        game = Game.objects.filter(id=self.game_id).first()
        if game.owner == user:
            game.winner = game.opponent
            game.owner_online = False
            game.opponent_online = False
        else:
            game.winner = game.owner
            game.owner_online = False
            game.opponent_online = False

    @database_sync_to_async
    def update(self, fen, pgn, checkmate):
        game = Game.objects.filter(id=self.game_id).first()
        if not game:
            print("Game not found")
            return
        game.fen = fen
        game.pgn = pgn
        if checkmate:
            game.winner = self.scope['user']
        game.save()