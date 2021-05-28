from math import *
import env

MATH_OPERATIONS = {
    'x': '*',
    ',': '',
    '^': '**',
    ' ': '',
    '%': '/100'
}

async def compute(ctx, expr):
    if expr:
        for math, code in MATH_OPERATIONS.items():
            expr = expr.replace(math, code)
    else:
        return
    try:
        value = eval(expr)
        if value is not None:
            value = '{:,}'.format(value).replace(',', ' ')
            if '.' in value:
                value = str(value).rstrip('0').rstrip('.')
            response = f'**=** `{value}`'
            await ctx.send(response)
    except Exception as e:
        await ctx.message.add_reaction('⁉️')
        if env.TESTING:
            import traceback
            traceback.print_exc()