import asyncio
from type import state, order, connection, visualization, instantActions


class TopicQueue:
    p_connection: asyncio.Queue[connection.Connection] = asyncio.Queue()
    p_visualization: asyncio.Queue[visualization.Visualization] = asyncio.Queue()
    p_state: asyncio.Queue[state.State] = asyncio.Queue()
    chanel_state: asyncio.Queue[state.State] = asyncio.Queue()
    p_order: asyncio.Queue[order.Order] = asyncio.Queue()
    p_instantActions: asyncio.Queue[instantActions.InstantActions] = asyncio.Queue()

    s_connection: asyncio.Queue[connection.Connection] = asyncio.Queue()
    s_visualization: asyncio.Queue[visualization.Visualization] = asyncio.Queue()
    s_state: asyncio.Queue[state.State] = asyncio.Queue()
    s_order: asyncio.Queue[order.Order] = asyncio.Queue()
    s_instantActions: asyncio.Queue[instantActions.InstantActions] = asyncio.Queue()


class EventLoop:
    event_loop = asyncio.get_event_loop()
