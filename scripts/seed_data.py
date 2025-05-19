import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import random
from datetime import datetime, timedelta

from faker import Faker

from app.db.session import async_session
from app.models import Chat, Group, Message, User
from app.models.chat import ChatType
from app.models.group import group_members

faker = Faker()


async def seed():
    async with async_session() as session:
        print("📥 Creating users...")
        users = [
            User(
                name=faker.first_name(), email=faker.unique.email(), password="hashedpw"
            )
            for _ in range(5)
        ]
        session.add_all(users)
        await session.flush()

        for u in users:
            print(f"👤 {u.name} ({u.email}) — ID: {u.id}")

        print("💬 Creating private chat...")
        private_chat = Chat(name="PrivateChat", type=ChatType.private)
        session.add(private_chat)
        await session.flush()
        print(f"🔗 Private chat ID: {private_chat.id}")

        session.add_all(
            [
                Message(
                    chat_id=private_chat.id,
                    sender_id=users[0].id,
                    text="Hi!",
                    timestamp=datetime.utcnow(),
                ),
                Message(
                    chat_id=private_chat.id,
                    sender_id=users[1].id,
                    text="Hello!",
                    timestamp=datetime.utcnow(),
                ),
            ]
        )

        print("👥 Creating group chat...")
        group_chat = Chat(name="GroupChat", type=ChatType.public)
        session.add(group_chat)
        await session.flush()

        group = Group(name="Test Group", chat_id=group_chat.id, owner_id=users[0].id)
        session.add(group)
        await session.flush()

        print(f"🔗 Group chat ID: {group_chat.id}")
        print(f"👑 Group created by: {users[0].name} (ID: {users[0].id})")

        for user in users:
            await session.execute(
                group_members.insert().values(group_id=group.id, user_id=user.id)
            )
        print(f"✅ Members added to group: {len(users)}")

        print("📝 Generating group messages...")
        for _ in range(10):
            sender = random.choice(users)
            session.add(
                Message(
                    chat_id=group_chat.id,
                    sender_id=sender.id,
                    text=faker.sentence(),
                    timestamp=datetime.utcnow()
                    - timedelta(minutes=random.randint(1, 60)),
                )
            )

        await session.commit()
        print("✅ Seed data created successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
