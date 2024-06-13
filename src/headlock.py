# ----------
# HOW TO USE:
# LINE 186 CHANGE movePerDegree TO CORRECT VALUE
# HOLD ALT TO TRACK TARGET
# V TO SWITCH TARGET
# CHANGE KEYS ON LINE 92 AND 93
# ----------
import keyboard, time, threading, sys, random, ctypes, math
from pynput.mouse import Controller, Button
from win32gui import GetWindowText, GetForegroundWindow
 
from offsets import *
import pyMeow as pm # type: ignore

mouse = Controller()
client = Client()



class Offsets:
    dwEntityList = client.offset('dwEntityList')
    dwLocalPlayerPawn = client.offset('dwLocalPlayerPawn')
    dwLocalPlayerController = client.offset('dwLocalPlayerController')
    dwViewMatrix = client.offset('dwViewMatrix')
    dwViewAngles = client.offset('dwViewAngles')

    m_pBoneArray = 480
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
        

    def bonePos(self, bone):
        gameScene = pm.r_int64(self.pr, self.entity + Offsets.m_pGameSceneNode)
        boneArrayPtr = pm.r_int64(self.pr, gameScene + Offsets.m_pBoneArray)

        return pm.r_vec3(self.pr, boneArrayPtr + bone * 32)

    def wts(self, viewMatrix):
        try:
            a, self.pos2d = pm.world_to_screen_noexc(viewMatrix, self.pos, 1)
            b, self.headPos2d = pm.world_to_screen_noexc(viewMatrix, self.bonePos(6), 1)
            
            if not a or not b:
                return False

            return True
        except:
            return False



class Colors:
    white = pm.get_color("white")
    black = pm.get_color("black")
    red = pm.get_color("#e03636")
    green = pm.get_color("#43e06d")

class CoClass:
    def __init__(self):
        self.pr = pm.open_process("cs2.exe") # process
        self.client = pm.get_module(self.pr, "client.dll")["base"] # client starting point

        self.mode = 0
        self.triggerKey = "alt"
        self.switchTarget = 'v'

        self.gettingId = False
        self.entIdList = []
        self.temp = 0
        
        print(f"Trigger key: {self.triggerKey.upper()}")


    def onoff(self):
        while True:
            if not GetWindowText(GetForegroundWindow()) == "Counter-Strike 2":
                self.mode = 0
                time.sleep(2)
                continue

            if keyboard.is_pressed(self.triggerKey):
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
            
            
            for ent in self.checkEnt(): 
                try:
                    while ent.health > 0:
                        if keyboard.is_pressed(self.switchTarget):
                            while keyboard.is_pressed(self.switchTarget):
                                pass
                            break
                        try:
                            if self.mode == 0:
                                raise
                            player = pm.r_int64(self.pr, self.client + Offsets.dwLocalPlayerPawn)
                            playerTeam = pm.r_int(self.pr, player + Offsets.m_iTeamNum)
                            if ent.team != playerTeam:  # NORMAL MATCHES
                            #if True: # DEATH MATCH
                                if ent.health > 0:
                                    selfpos = pm.r_vec3(self.pr, player + Offsets.m_vOldOrigin)
                                    self.hl(ent.position, selfpos)
                                else:
                                    break
                        except:
                            time.sleep(0.01)

                        time.sleep(0.01)
                except:
                    pass
                
        
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
        moveViewYaw = int((targetYaw-yaw) * movePerDegree)
        ctypes.windll.user32.mouse_event(
            ctypes.c_uint(0x0001),
            ctypes.c_uint(-moveViewYaw),
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
                pm.draw_text('ACTIVATED', 1150, 0, 50, Colors.white)
            else:
                pm.draw_text('DEACTIVATED', 1100, 0, 50, Colors.white)

            if self.gettingId == True:
                pm.draw_text('Getting Players IDs...', 50, 0, 20, Colors.white)
            else:
                pass


            pm.end_drawing()
            
    def checkEnt(self):
        entList = pm.r_int64(self.pr, self.client + Offsets.dwEntityList)

        if len(self.entIdList) > 0:
            for i in self.entIdList:
                try:
                    entEntry = pm.r_int64(self.pr, entList + 0x8 * (i >> 9) + 0x10)
                    entity = pm.r_int64(self.pr, entEntry + 120 * (i & 0x1FF))
                except:
                    continue
                yield Entity(self.pr, entity)

    def checkEnttoo(self):
        entList = pm.r_int64(self.pr, self.client + Offsets.dwEntityList)


        for i in self.entIdList:
            try:
                entEntry = pm.r_int64(self.pr, entList + 0x8 * (i >> 9) + 0x10)
                entity = pm.r_int64(self.pr, entEntry + 120 * (i & 0x1FF))


                
            except:
                continue
            yield Entity(self.pr, entity)


    def getEntId(self):
        while True:
            if not GetWindowText(GetForegroundWindow()) == "Counter-Strike 2":
                time.sleep(2)
                continue

            #if keyboard.is_pressed(self.getEntIdKey):
            if True:
                self.entIdList = []
                self.gettingId = True
                try:
                    player = pm.r_int64(self.pr, self.client + Offsets.dwLocalPlayerPawn)
                    playerTeam = pm.r_int(self.pr, player + Offsets.m_iTeamNum)
                except:
                    pass
                for i in range(1, 5000):
                    try:
                        entList = pm.r_int64(self.pr, self.client + Offsets.dwEntityList)
                        entEntry = pm.r_int64(self.pr, entList + 0x8 * (i >> 9) + 0x10)
                        entity = pm.r_int64(self.pr, entEntry + 120 * (i & 0x1FF))
                        entTeam = pm.r_int(self.pr, entity + Offsets.m_iTeamNum)
                        if pm.r_int(self.pr, entity + Offsets.m_iHealth) == 0:
                            continue
                        

                        if entTeam != playerTeam:  # NORMAL MATCHES / ONLY ENEMY HP
                        #if True: # DEATH MATCH / TEAM HEALTH
                            self.entIdList.append(i)
                    except:
                        pass
                time.sleep(0.5)
                self.gettingId = False

            time.sleep(10)

   
        
if __name__ == '__main__':
    print('Connecting...')
    time.sleep(1)
    os.system('cls')
    coclass = CoClass()

    cet = threading.Thread(target=coclass.getEntId)
    oot = threading.Thread(target=coclass.onoff)
    tbt = threading.Thread(target=coclass.triggerBot)
    pt = threading.Thread(target=coclass.paint)

    

    cet.start()
    oot.start()
    tbt.start()
    pt.start()

    cet.join()
    oot.join()
    tbt.join()
    pt.join()

    


