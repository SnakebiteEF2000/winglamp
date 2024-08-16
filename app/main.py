import ujson
from machine import Pin
from neopixel import NeoPixel
from microdot import Microdot, send_file, Response
import uasyncio
import ugit
from urlcode import unquote
import math
import senko

# Setup neopixels
LED_PIN = 6
NUM_LEDS = 235
LEADER = False
CONFIG_FILE = 'config.json'

OTA = senko.Senko(
    user="SnakebiteEF2000", repo="winglamp",branch="main", files=["www/admin.html","www/index.html", "boot.py", "main.py", "microdot.py", "urlcode.py"]
)
color = (50,50,50)
color2 = (70,70,70)
pixels = NeoPixel(Pin(LED_PIN), NUM_LEDS)

# setup web server
app = Microdot()
Response.default_content_type = 'application/json'
current_task = None


# webserver routes
@app.before_request
async def pre_request_handler(request):
   if current_task:
      current_task.cancel()

@app.route('/')
async def index(request):
    return send_file('/www/index.html', max_age=86400)

@app.route('/admin')
async def index(request):
    return send_file('/www/admin.html', max_age=86400)

@app.route('/makeupdate')
async def index(request):
    import senko
    import machine

    if OTA.update():
        setRGB((100,100,0),100)

    machine.reset()


@app.route('/gitupdate')
async def index(request):
    ugit.pull_all(isconnected=True)

@app.route('setwifi')
async def index(request):
    import machine
    ussid = unquote(request.args['ssid'])
    upassword = unquote(request.args['password'])
    #Debug
    print(ussid, upassword)
    setRGB((0,0,0),0)
    setWifi(CONFIG_FILE,ussid,upassword)
    machine.reset()
    return

@app.route('/setEffect')
async def set_effect(request):
    global current_task
    effect = request.args['effect']
    if effect == 'rainbow':
        current_task = uasyncio.create_task(rainbow())
        return {'status': 'ok'}
    elif effect == 'purple_beam':
        current_task = uasyncio.create_task(purple_beam())
        return {'status': 'ok'}
    else:
        return {'status': 'error', 'message': 'Effect not available'}


@app.get('/rgb')
async def rgb(request):
    setRGB((int(request.args['r']), int(request.args['g']), int(request.args['b'])), int(request.args['brightness']))
    return 'OK'

# effects
async def rainbow():
    def wheel(pos):
        # Generate rainbow colors across 0-255 positions.
        if pos < 85:
            return (255 - pos * 3, pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return (0, 255 - pos * 3, pos * 3)
        else:
            pos -= 170
            return (pos * 3, 0, 255 - pos * 3)

    while True:
        for j in range(256):
            for i in range(NUM_LEDS):
                pixel_index = (i * 256 // NUM_LEDS) + j
                color = wheel(pixel_index & 255)
                pixels[i] = color
            pixels.write()
            await uasyncio.sleep_ms(50)

def getWindow(start,width, end):
    window = []
    for i in range(width):
        window.append((start+i)%end)
    return window

async def purple_beam():
    #beam_color = (128, 0, 128)  # Purple color
    #beam_width = 10  # Width of the purple beam

    while True:
        for i in range(NUM_LEDS):
            arr = getWindow(i, 10, NUM_LEDS)

            midd = len(arr)//2

        for i in range(len(arr[:midd])):
            RGB= (int(color[0]*(10+(i*30))/100),int(color[1]*(10+(i*30))), int(color[2]*(10+(i*30))))
            res = arr[:midd]
            res1 = res[::-1]
            n = res1[i]
            pixels[n] = RGB

        if LEADER == True:
            for i in range(len(arr[midd:])):
                RGB1= (int(color[0]*(10+(i*30))/100),int(color[1]*(10+(i*30))), int(color[2]*(10+(i*30))))
                res = arr[midd:]
                n = res[i]
                pixels[n] = RGB1

            pixels.write()
            await uasyncio.sleep_ms(1000)
            pixels.fill((0,0,0))

# set RGB colour
def setRGB(rgb_tuple, brightness):
    r, g, b = rgb_tuple
    brightness = int(brightness / 100 * 255)

    r = int(r * brightness / 255)
    g = int(g * brightness / 255)
    b = int(b * brightness / 255)

    for i in range(NUM_LEDS):
        pixels[i] = (r,g,b)
    pixels.write()

def setWifi(config_file,ssid, password):
    try:
        with open(config_file, 'r') as f:
            config = ujson.load(f)
    except OSError as e:
        return ("Error opening file:",e)

    config['wifi']['ssid'] = ssid
    config['wifi']['password'] = password

    try:
        with open(config_file, 'w') as f:
            ujson.dump(config, f)
        return ("Wifi configuration updated successfully.")
    except OSError as e:
        return ("Error writing config file:",e)


def main():
    #startup effect
    setRGB((255,80,255), 30)
    #ip_binary()

    print("Server up!")
    try:
       app.run(port=80)
    except:
       app.shutdown()

if __name__ == "__main__":
    main()
