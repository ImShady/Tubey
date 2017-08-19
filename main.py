from flask import request, jsonify, Flask, make_response
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
    print(request.form)

    tubey.verify_token(token)

    channel = request.form.get('channel_id', None)
    user = request.form.get('user_id', None)
    text = request.form.get('text', None)

    tubey.suggest_video(text, channel, user, is_shuffle=False)

    return make_response("", 200)

@app.route('/callback', methods=['POST'])
def button_click():
    payload = json.loads(request.form.get('payload', None))
    print(payload)

    tubey.verify_token(payload['token'])

    button = payload['actions'][0]
    button_type = button['name']
    button_value = button['value']
    button_index = button['index']

    result = {}

    if button_type == 'shuffle':
        text = button_value
        result = tubey.suggest_video(text, payload['channel']['id'], payload['user']['id'], is_shuffle=True)
    elif button_type == 'next':
        text = button_value
        result = tubey.suggest_video(text, payload['channel']['id'], payload['user']['id'], is_next=True, index=button_index)
    elif button_type == 'send':
        result = tubey.send_video(user=payload['user']['name'], video_id=button_value, channel=payload['channel']['id'])
    elif button_type == 'cancel':
        result = {"delete_original": True}

    return jsonify(result)

if __name__ == "__main__":
    context = (Config.get_variable('ssl_cert', 'chain'), Config.get_variable('ssl_cert', 'privkey'))
    host = Config.get_variable('server_details', 'host')
    port = int(Config.get_variable('server_details', 'port'))
    app.run(port=port, host=host, ssl_context=context, debug=True)
