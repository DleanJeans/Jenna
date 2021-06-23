import pytest
from cogs import dank


@pytest.mark.asyncio
async def test_unscramble(mocker):
    INPUT = 'earriragoyhpxod'
    EXPECTED = 'xeroradiography'

    mocker.patch('cogs.dank.unscramble', return_value=[EXPECTED])

    content = f'Scramble: `{INPUT}`'
    answer = await dank.solve_minigame(content)
    assert answer == EXPECTED