from flask import Flask, request, jsonify
app = Flask(__name__)

CPMs = {}

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/update', methods=['get'])
def update_info():
    name = request.args.get("name", None)
    radius = request.args.get("radius", None)
    speed = request.args.get("speed", None)
    CPMs[name] = {'name':name,'radius':radius,'speed':speed}
    print(CPMs)
    return {"response": "received"}

@app.route('/retrieve', methods=['get'])
def retrieve_info():
    return CPMs

if __name__ == '__main__':
    app.run()