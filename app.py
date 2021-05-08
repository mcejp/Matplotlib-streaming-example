from flask import Flask, render_template_string, Response
import pika


app = Flask(__name__)
app.config["exchange_name"] = "hello_world"


@app.route("/")
def index():
    return render_template_string("""\
<html>
  <head>
    <title>Matplotlib streaming demonstration</title>
  </head>
  <body>
    <h1>Matplotlib streaming demonstration</h1>
    <img id="bg" src="{{ url_for('video_feed') }}">
  </body>
</html>
""")


def gen():
    with pika.BlockingConnection(pika.ConnectionParameters("localhost")) as connection:
        channel = connection.channel()

        result = channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange=app.config["exchange_name"], queue=queue_name)

        for method, properties, body in channel.consume(queue=queue_name):
            yield (
                b"--frame\r\n" b"Content-Type: " + properties.content_type.encode() + b"\r\n\r\n" + body + b"\r\n\r\n"
            )
            channel.basic_ack(method.delivery_tag)


@app.route("/video_feed")
def video_feed():
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")
