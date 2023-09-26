import asyncio
from type import state, order, connection, visualization, instantActions,pushMsgType,factsheet


class TopicQueue:
    p_connection: asyncio.Queue[connection.Connection] = asyncio.Queue(3)
    p_visualization: asyncio.Queue[visualization.Visualization] = asyncio.Queue(3)
    p_state: asyncio.Queue[state.State] = asyncio.Queue(3)
    chanel_state: asyncio.Queue[state.State] = asyncio.Queue(3)
    p_order: asyncio.Queue[order.Order] = asyncio.Queue(3)
    p_instantActions: asyncio.Queue[instantActions.InstantActions] = asyncio.Queue(3)

    s_connection: asyncio.Queue[connection.Connection] = asyncio.Queue(3)
    s_visualization: asyncio.Queue[visualization.Visualization] = asyncio.Queue(3)
    s_state: asyncio.Queue[state.State] = asyncio.Queue(3)
    s_order: asyncio.Queue[order.Order] = asyncio.Queue(3)
    s_instantActions: asyncio.Queue[instantActions.InstantActions] = asyncio.Queue(3)
    s_factSheet: asyncio.Queue[factsheet.Factsheet] = asyncio.Queue(3)

    pushData = asyncio.Queue(3)


class EventLoop:
    event_loop = asyncio.get_event_loop()
