from fastapi import FastAPI


app = FastAPI(
    title='Todo API',
    description='A modern task & project management API',
    version='0.1.0'
)


@app.get('/')
async def read_root():
    return {'message': 'Welcome to Todo API'}
