from flask import request, jsonify, abort, Flask, make_response
from lib.config import Config
from lib.slack import Tubey
import json

# Detailed documentation of Slack slash commands:
# https://api.slack.com/slash-commands

app = Flask(__name__)

# The parameters included in a slash command request (with example values):
#   token=gIkuvaNzQIHg97ATvDxqgjtO
#   team_id=T0001
#   team_domain=example
#   channel_id=C2147483705
#   channel_name=test
#   user_id=U2147483697
#   user_name=Steve
#   command=/weather
#   text=94070
#   response_url=https://hooks.slack.com/commands/1234/5678

tubey = Tubey()

@app.route('/tubey', methods=['POST'])
def slash_command():
    # Parse the command parameters, validate them, and respond
    token = request.form.get('token', None)
    verif_token = Config.get_variable('tubey', 'verif_token')
    print(request.form)

    # Validate the request parameters
    if token != verif_token:
        abort(401)  # Unauthorized request. If you're not Slack, go away

    channel = request.form.get('channel_id', None)
    user = request.form.get('user_id', None)
    text = request.form.get('text', None)


    tubey.suggest_video(text, channel, user, is_shuffle=False)

    return make_response("", 200)

@app.route('/callback', methods=['POST'])
def button_click():
    payload = json.loads(request.form.get('payload', None))
    print(payload)

    verif_token = Config.get_variable('tubey', 'verif_token')

    if payload['token'] != verif_token:
        abort(401)

    button = payload['actions'][0]
    button_type = button['name']
    button_value = button['value']

    result = {}

    if button_type == 'shuffle':
        text = button_value
        result = tubey.suggest_video(text, payload['channel']['id'], payload['user']['id'], is_shuffle=True)
    elif button_type == 'send':
        result = tubey.send_video(channel=payload['channel']['id'], video_id=button_value)
    elif button_type == 'cancel':
        #TODO: Implement cancel
        print("write me plz")

    return jsonify(result)

if __name__ == "__main__":
    context = (Config.get_variable('ssl_cert', 'chain'), Config.get_variable('ssl_cert', 'privkey'))
    host = Config.get_variable('server_details', 'host')
    port = int(Config.get_variable('server_details', 'port'))
    app.run(port=port, host=host, ssl_context=context, debug=True)
