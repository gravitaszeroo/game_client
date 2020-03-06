import curses
import requests
import json
import keyboard
from curses import wrapper
from time import sleep

FPS = 5
<<<<<<< HEAD
=======
ROOM_WIDTH = 120
ROOM_HEIGHT = 28
>>>>>>> f24e9e538afffe83495d27db7d5e42bb95813509

# specify username
username = input("username? >")

body = {"username":username,
 "password1":"testpassword",
 "password2":"testpassword"}

# connect to a server
server_choice = None

hosts = {
"local":"http://127.0.0.1:8000",
"web":"https://mudserver.herokuapp.com",
'rob-web':"https://lambda-mud-buildweek.herokuapp.com"
}

while server_choice not in hosts.keys():
    server_choice = input("Which Server? (local/web/rob-web) >")
host = hosts[server_choice]

# register user
headers = {"Content-Type":"application/json"}
r = requests.post(host+"/api/registration/", data=body)
print(r.status_code)
#import pdb; pdb.set_trace()
response = json.loads(r.text)
key = response['key']

# start game
headers = {"Authorization":f"Token {key}"}
s = requests.get(host+"/api/adv/init/", headers=headers)
print(s.status_code)
print(s.text)


def room_screen(stdscr):
    # sc = curses.initscr()
    # h, w = sc.getmaxyx()
    # win = curses.newwin(h, w, 0, 0)
    # win.keypad(1)
    curses.curs_set(0)
    #
    # stdscr.addch(1, 1, curses.ACS_DIAMOND)

    height, width = stdscr.getmaxyx()
    keypress = 'f'
    player_x = int(width // 2)
    player_y = int((height // 2) + 3)

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Don't wait for keypresses
    stdscr.nodelay(True)

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # move around the room
    while keypress != ord('q'):
        # Initialization
        stdscr.clear()

        # TODO: add compensation for lag



        if keypress == curses.KEY_DOWN:
            player_y = player_y + 1
        elif keypress == curses.KEY_UP:
            player_y = player_y - 1
        elif keypress == curses.KEY_RIGHT:
            player_x = player_x + 1
        elif keypress == curses.KEY_LEFT:
            player_x = player_x - 1

        # restrict movement to screen
        player_x = max(0, player_x)
        player_x = min(width-1, player_x)
        player_y = max(0, player_y)
        player_y = min(height-1, player_y)

        # Update the server, get room
        data = {"x":player_x, "y":player_y}
        r = requests.post(host+"/api/adv/get_room",
                            json=data, headers=headers)
        # if r.status_code not in [200, 201]:
        #     print(r.status_code)
        response = json.loads(r.text)

        # sync player location
        player_x = response['x']
        player_y = response['y']

        # Declaration of strings
        title = str(response['title'])[:width-1]
        subtitle = str(response['description'])[:width-1]
        scores = str(response['scores'])
        statusbarstr = "Press 'q' to exit | STATUS BAR | Pos: {}, {}".format(player_x, player_y)

        # Centering text
        start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
        start_x_subtitle = int((width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
        start_y = int((height // 2) - 10)

        # Show width and height
        whstr = "Width: {}, Height: {}".format(width, height)
        stdscr.addstr(0, 0, whstr, curses.color_pair(1))
        # show keypress
        stdscr.addstr(1, 0, str(keypress), curses.color_pair(1))

        # Render status bar
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height-2, 0, statusbarstr)
        stdscr.addstr(height-2, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(3))

        # Display map objects
        for _y, row in enumerate(response['room_array']):
            for _x, char in enumerate(row):
                if row[_x] != '`':
                    stdscr.addch(_y, _x, char[:1])


        # List players in current room
        players_list = "Players: {}".format(', '.join(response['players']))
        stdscr.addstr(29, 0, players_list[:width-1], curses.color_pair(1))

        # Turning on attributes for title
        stdscr.attron(curses.color_pair(2))
        stdscr.attron(curses.A_BOLD)

        # Rendering title
        stdscr.addstr(start_y, start_x_title, title)

        # Turning off attributes for title
        stdscr.attroff(curses.color_pair(2))
        stdscr.attroff(curses.A_BOLD)


        # Display other players
        for i in response['players'].keys():
            try:
                stdscr.addch(response['players'][i]['y'], response['players'][i]['x'], 'a')
            except:
                pass

        # Display creatures
        for i in response['creatures'].keys():
            try:
                stdscr.addch(response['creatures'][i]['y'], response['creatures'][i]['x'], 'Q')
            except Exception as e:
                # WATCH FOR INVISIBLE MONSTERS
                print(i)
                raise(e)

        # Print rest of text
        stdscr.addstr(start_y + 1, start_x_subtitle, subtitle)
        stdscr.addstr(start_y + 3, (width // 2) - 2, '-' * 4)
        stdscr.addstr(30, 0, scores, curses.color_pair(2))
        stdscr.addch(player_y, player_x, '@')
        


        # Refresh the screen
        stdscr.refresh()

        # get next input, restricting to FPS
        sleep(1/FPS)
        keypress = stdscr.getch()

try:
    wrapper(room_screen)
except Exception as e:
    # Show the user how to resize their terminal window
    print(e)
    print("-" * (ROOM_WIDTH+1))
    for i in range(ROOM_HEIGHT+1):
        if i == ROOM_HEIGHT // 2:
            print(" "*50, "~ EMBIGGEN YOUR WINDOW ~")
            print(" "*50, " ~ or see above error ~")
        else:
            print("|")

