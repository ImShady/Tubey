from flask import request, jsonify, abort, Flask
from lib.config import Config
from lib.slack import Tubey

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

@app.route('/tubey', methods=['POST'])
def slash_command():
    # Parse the command parameters, validate them, and respond
    token = request.form.get('token', None)
    # command = request.form.get('command', None) -- may eventually need this
    text = request.form.get('text', None)

    verif_token = Config.get_variable('tubey', 'verif_token')

    # Validate the request parameters
    if token != verif_token:
        abort(401) # Unauthorized request. If you're not Slack, go away

    tubey = Tubey()
    videos = tubey.search(text)

    suggestion = jsonify(
        {'response_type': 'in_channel',
         "attachments": [
             {
                 'text': "https://www.youtube.com/watch?v={}".format(videos[0]['id']),
                 "fallback": "You did not choose a video to send.",
                 "color": "#CD201F",
                 "attachment_type": "default",
                 "actions": [
                     {"name": "submit",
                     "text": "Send",
                     "type": "button",
                     "styke": "primary",
                     "value": "send"
                    },
                    {"name": "cancel",
                     "text": "Cancel",
                     "type": "button",
                     "value": "cancel"
                    }]
             }]
         })

    # See api.slack.com/docs/formatting and api.slack.com/docs/attachments to send richly formatted messages
    return suggestion
    # return jsonify({
    #     'response_type': 'in_channel',
    #     'text': "Look at me I'm responding from the server!",
    #     'attachments': []
    # })

if __name__ == "__main__":
    context = (Config.get_variable('ssl_cert', 'chain'), Config.get_variable('ssl_cert', 'privkey'))
    host = Config.get_variable('server_details', 'host')
    port = int(Config.get_variable('server_details', 'port'))
    app.run(port=port, host=host , ssl_context=context, debug=True)
