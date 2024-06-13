import keyboard, time, threading, sys, random, ctypes, math, os
from pynput.mouse import Controller, Button
from win32gui import GetWindowText, GetForegroundWindow
 
from offsets import *
import pyMeow as pm 

mouse = Controller()
client = Client()



class Offsets:
    dwEntityList = client.offset('dwEntityList')
    dwLocalPlayerPawn = client.offset('dwLocalPlayerPawn')
    dwLocalPlayerController = client.offset('dwLocalPlayerController')
    dwViewMatrix = client.offset('dwViewMatrix')
    dwViewAngles = client.offset('dwViewAngles')


    m_pGameSceneNode = client.clientdll('C_BaseEntity', 'm_pGameSceneNode')
    m_vecVelocity = client.clientdll('C_BaseEntity', 'm_vecVelocity')
    m_iIDEntIndex = client.clientdll('C_CSPlayerPawnBase', 'm_iIDEntIndex')
    m_iTeamNum = client.clientdll('C_BaseEntity', 'm_iTeamNum')
    m_iHealth = client.clientdll('C_BaseEntity', 'm_iHealth')
    m_iszPlayerName = client.clientdll('CBasePlayerController', 'm_iszPlayerName')
    m_hPlayerPawn = client.clientdll('CCSPlayerController', 'm_hPlayerPawn')
    m_vOldOrigin = client.clientdll('C_BasePlayerPawn', 'm_vOldOrigin')

class Entity:
    def __init__(self, pr, entity):
        self.pr = pr
        self.entity = entity

    @property
    def health(self):
        return pm.r_int(self.pr, self.entity + Offsets.m_iHealth)
    
    @property
    def team(self):
        return pm.r_int(self.pr, self.entity + Offsets.m_iTeamNum)
    
    @property
    def position(self):
        return pm.r_vec3(self.pr, self.entity + Offsets.m_vOldOrigin)
    
    @property
    def velocity(self):
        return pm.r_float(self.pr, self.entity + Offsets.m_vecVelocity)
        



class Colors:
    white = pm.get_color("white")
    black = pm.get_color("black")


class Pyhl:
    def __init__(self):
        self.pr = pm.open_process("cs2.exe") # process
        self.client = pm.get_module(self.pr, "client.dll")["base"] # client starting point

        self.mode = 0
        self.triggerKey = "alt"
        
        print(f"Trigger key: {self.triggerKey.upper()}")


    def onoff(self):
        while True:
            if not GetWindowText(GetForegroundWindow()) == "Counter-Strike 2":
                self.mode = 0
                time.sleep(2)
                continue

            if keyboard.is_pressed(self.triggerKey):
                while keyboard.is_pressed(self.triggerKey):
                    pass
                if self.mode == 0:
                    self.mode = 1
                else: 
                    self.mode = 0
            time.sleep(0.15)
    
    def triggerBot(self):
        while True:
            if not GetWindowText(GetForegroundWindow()) == "Counter-Strike 2":
                time.sleep(2)
                continue    

            if self.mode == 0:
                time.sleep(0.3)
                continue
            

            try:
                player = pm.r_int64(self.pr, self.client + Offsets.dwLocalPlayerPawn)
                entityId = pm.r_int(self.pr, player + Offsets.m_iIDEntIndex)

                if entityId > 0:
                    entList = pm.r_int64(self.pr, self.client + Offsets.dwEntityList)
                    entEntry = pm.r_int64(self.pr, entList + 0x8 * (entityId >> 9) + 0x10)
                    entity = pm.r_int64(self.pr, entEntry + 120 * (entityId & 0x1FF))
                    ent = Entity(self.pr, entity)

                    playerTeam = pm.r_int(self.pr, player + Offsets.m_iTeamNum)

                    if ent.team != playerTeam:  # NORMAL MATCHES
                    #if True: # DEATH MATCH
                        if ent.health > 0: 
                            selfpos = pm.r_vec3(self.pr, player + Offsets.m_vOldOrigin)
                            self.hl(ent.position, selfpos)
                                
                            time.sleep(0.01)
                            mouse.press(Button.left)
                            time.sleep(0.02)
                            mouse.release(Button.left)
                time.sleep(0.03)
            except:
                time.sleep(0.03)

    def headlock(self, entpos, selfpos):
         
        
        selfx = selfpos['x']
        selfy = selfpos['y']
        selfz = selfpos['z']
        entx = entpos['x']
        enty = entpos['y']
        entz = entpos['z']

        xydistance = math.sqrt((entx - selfx) ** 2 + (enty - selfy) ** 2)
        zdistance = entz - selfz
        tan_theta = zdistance / xydistance
        targetPitch = -math.atan(tan_theta) * (180/math.pi)

        sin_theta = (enty - selfy) / math.sqrt((entx - selfx) ** 2 + (enty - selfy) ** 2)
        theta = math.asin(sin_theta) * (180/math.pi)
        if entx - selfx < 0:
            theta = 180 - theta

        targetYaw = theta # - viewAngle[1]
        while targetYaw > 180:
            targetYaw -= 360
        while targetYaw < -180:
            targetYaw += 360

        return targetPitch, targetYaw

    def hl(self, entpos, selfpos):
        # moveperdegree = 100 / sensitivity * 2.2

        movePerDegree = 100 / 2.2

        viewAngle = pm.r_floats(self.pr, self.client + Offsets.dwViewAngles, 3) # PITCH, YAW, ROLL
        pitch = viewAngle[0]
        yaw = viewAngle[1]
        targetPitch, targetYaw = self.headlock(entpos, selfpos)
        moveViewPitch = int((targetPitch-pitch) * movePerDegree)
        moveViewYaw = int((yaw-targetYaw) * movePerDegree)
        ctypes.windll.user32.mouse_event(
            ctypes.c_uint(0x0001),
            ctypes.c_uint(moveViewYaw),
            ctypes.c_uint(moveViewPitch),
            ctypes.c_uint(0),
            ctypes.c_uint(0)
        )
      
    def paint(self):
        pm.overlay_init(fps=144)
        while pm.overlay_loop():
            time.sleep(0.3)
            pm.begin_drawing()
            if not GetWindowText(GetForegroundWindow()) == "Counter-Strike 2":
                pm.end_drawing()
                time.sleep(2)
                continue

            if self.mode == 1:
                pm.draw_text('ON', 1250, 0, 50, Colors.white)
            else:
                pm.draw_text('OFF', 1200, 0, 50, Colors.white)

            pm.end_drawing()
        
if __name__ == '__main__':
    print('Connecting...')
    time.sleep(1)
    os.system('cls')
    pyhl = Pyhl()

    oot = threading.Thread(target=pyhl.onoff)
    tbt = threading.Thread(target=pyhl.triggerBot)
    pt = threading.Thread(target=pyhl.paint)


    oot.start()
    tbt.start()
    pt.start()

    oot.join()
    tbt.join()
    pt.join()

    


