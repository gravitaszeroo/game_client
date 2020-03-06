import curses
import requests
import json
import keyboard
from curses import wrapper
from time import sleep

FPS = 5

# specify username
username = input("username? >")

body = {"username":username,
 "password1":"testpassword",
 "password2":"testpassword"}

# connect to a server
server_choice = None
GAME_WIDTH = 60
GAME_HEIGHT = 28
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

ITEM_CHARS = ['$','€','¥']

def room_screen(stdscr):

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)


    curses.curs_set(0)
    height, width = stdscr.getmaxyx()
    keypress = 'f'
    player_x = int(GAME_WIDTH // 2)
    player_y = int((GAME_HEIGHT // 2) + 3)

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Don't wait for keypresses
    stdscr.nodelay(True)

    

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
        scores = response['scores']
        statusbarstr = "Press 'q' to exit | STATUS BAR | Pos: {}, {}".format(player_x, player_y)

        # Centering text
        start_x_title = int(GAME_WIDTH+2)
        start_x_subtitle = int(GAME_WIDTH+2)
        start_y = int(2)

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
                if row[_x] in ITEM_CHARS:
                    stdscr.attron(curses.color_pair(4))
                    stdscr.attron(curses.A_BOLD)
                    stdscr.addch(_y, _x, char[:1])
                    stdscr.attroff(curses.color_pair(4))
                    stdscr.attroff(curses.A_BOLD)
                    


       

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
                stdscr.attron(curses.color_pair(5))
                stdscr.attron(curses.A_BOLD)
                stdscr.addch(response['players'][i]['y'], response['players'][i]['x'], '*')
                stdscr.attroff(curses.color_pair(5))
                stdscr.attroff(curses.A_BOLD)
                
            except:
                pass

        # Display creatures
        for i in response['creatures'].keys():
            try:
                stdscr.attron(curses.color_pair(2))
                stdscr.attron(curses.A_BOLD)
                stdscr.addch(response['creatures'][i]['y'], response['creatures'][i]['x'], 'Q')
                stdscr.attroff(curses.color_pair(2))
                stdscr.attroff(curses.A_BOLD)
            except Exception as e:
                # WATCH FOR INVISIBLE MONSTERS
                print(i)
                raise(e)
    
        # Print rest of text
        start_y +=1
        stdscr.addstr(start_y, start_x_subtitle, subtitle)
        start_y +=1
        stdscr.addstr(start_y, (width // 2) - 2, '-' * 4)
        start_y +=1
        #stdscr.addstr(start_y, 0, str(len(scores)), curses.color_pair(2))
        stdscr.attron(curses.color_pair(6))
        stdscr.attron(curses.A_BOLD)
        stdscr.addch(player_y, player_x, '@')
        stdscr.attroff(curses.color_pair(6))
        stdscr.attroff(curses.A_BOLD)
        
        #Print current player score
        start_y += 1
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(start_y, start_x_title, "Current Score:", curses.color_pair(3))
        stdscr.addstr(start_y, start_x_title+len("Current Score")+3, str(scores[-1]), curses.color_pair(4))
        stdscr.attroff(curses.A_BOLD)

        # List players in current room with scores
        #players_list = "Players: {}".format(', '.join(response['players']))
        players_list = response['players']
        i = 0
        start_y += 3
        stdscr.addstr(start_y, start_x_title, "Players here:", curses.color_pair(3))
        for player in players_list:
            start_y += 1
            stdscr.addstr(start_y, start_x_title, player, curses.color_pair(1))
            stdscr.addstr(start_y, start_x_title+len(player)+2, str(scores[i]), curses.color_pair(1))
            i +=1
            if i > 10:
                break

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
    print("-" * (GAME_WIDTH+1))
    for i in range(GAME_HEIGHT+1):
        if i == GAME_HEIGHT // 2:
            print(" "*50, "~ EMBIGGEN YOUR WINDOW ~")
            print(" "*50, " ~ or see above error ~")
        else:
            print("|")

