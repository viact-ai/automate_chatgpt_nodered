import json
import re


def fix_json_with_js_code(json_string):
    # Check if the string is already valid JSON
    try:
        parsed_json = json.loads(json_string)
        return parsed_json
    except json.JSONDecodeError:
        pass

    # Define a regular expression to match JavaScript code blocks
    js_code_regex = re.compile(
        r'(?<!\\)"((?<!\\)\\(?!n|r|t|u)|(?<!\\)(?s:.)*?(?<!\\))(?<!\\)"')

    # Replace JavaScript code blocks with escaped versions
    def escape_js_code(match):
        code = match.group(1)
        return '"' + code.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'
    fixed_json = js_code_regex.sub(escape_js_code, json_string)

    # Parse the fixed JSON string
    parsed_json = json.loads(fixed_json)
    return parsed_json


def main():
    # a = """
    #     [{"id":"9b1a9a2a.8caed8","type":"inject","z":"c5fc3d5d.3ad798","name":"","props":[{"p":"payload"},{"p":"topic","vt":"str"}],"repeat":"1800","crontab":"","once":true,"onceDelay":"","topic":"","payload":"","payloadType":"date","x":130,"y":160,"wires":[["b15de287.d422f","e42ad6d.b0a3a3"]]},{"id":"b15de287.d422f","type":"function","z":"c5fc3d5d.3ad798","name":"","func":"msg.location = {\n    latitude: \"\", \n    longitude:\"\"\n}\nmsg.temperature = 25;\nmsg.humidity = 50;\nreturn msg;","outputs":1,"noerr":0,"initialize":"","finalize":"","x":310,"y":220,"wires":[["8188e5e5.5c5998"]]},{"id":"e42ad6d.b0a3a3","type":"http request","z":"c5fc3d5d.3ad798","name":"","method":"GET","ret":"txt","paytoqs":"ignore","url":"https://api.openweathermap.org/data/2.5/weather?q=London,uk&appid=APIKEY","tls":"","persist":false,"proxy":"","authType":"","x":330,"y":160,"wires":[["8188e5e5.5c5998"]]},{"id":"8188e5e5.5c5998","type":"function","z":"c5fc3d5d.3ad798","name":"parse weather data","func":"msg.forecast = {\n    temp: 25,\n    feels_like: 25,\n    humidity: 50,\n    wind_speed: 5\n}\nreturn msg;","outputs":1,"noerr":0,"initialize":"","finalize":"","x":530,"y":220,"wires":[["f36d6e00.0c617"]]},{"id":"f36d6e00.0c617","type":"function","z":"c5fc3d5d.3ad798","name":"make prediction","func":"if(msg.forecast.temp<20){ //bad weather\n    msg.alert = {\n        subject: \"Tomorrow weather\",\n        message: \"Tomorrow weather will be bad, please prepare.\"\n    }\n}\nreturn msg;","outputs":1,"noerr":0,"initialize":"","finalize":"","x":780,"y":220,"wires":[["dbcf54e7.2d2c1"]]},{"id":"dbcf54e7.2d2c1","type":"switch","z":"c5fc3d5d.3ad798","name":"","property":"alert","propertyType":"msg","rules":[{"t":"nnull"},{"t":"else"}],"checkall":"true","repair":false,"outputs":2,"x":930,"y":220,"wires":[["2b345ff5.317cde"],["5a5a5a5.2793b7c"]]},{"id":"2b345ff5.317cde","type":"email","z":"c5fc3d5d.3ad798","server":"smtp.gmail.com","port":"465","secure":true,"tls":{"ciphers":"SSLv3"},"name":"","dname":"","x":1180,"y":160,"wires":[]},{"id":"5a5a5a5.2793b7c","type":"debug","z":"c5fc3d5d.3ad798","name":"","active":true,"tosidebar":true,"console":false,"tostatus":false,"complete":"false","statusVal":"","statusType":"auto","x":1090,"y":280,"wires":[]}]
    # """
    data = fix_json_with_js_code(a.strip())
    print(data)


if __name__ == "__main__":
    main()
