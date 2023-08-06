from my_module import Bot

from servicefoundry.v2.python_service import PythonService, remote

bot_service = PythonService(name="bot-service", port=4000)

bot_service.register_class(
    remote(Bot, init_kwargs={"bot_name": "Alice"}, name="alice_bot")
)
bot_service.register_class(remote(Bot, init_kwargs={"bot_name": "Bob"}, name="bob_bot"))

bot_service.deploy("v1:local:my-ws-2")
# bot_service.run()
#
# print(bot_service)
#
# another_bot_service = PythonService(name="another_bot_service", port=4001)
# another_bot_service.register_class(
#     remote(Bot, init_kwargs={"bot_name": "Rob"}, name="rob_bot")
# )
# another_bot_service.run().join()
