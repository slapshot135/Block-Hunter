import pygame, math
from pygame.locals import *
from random import randint as rand
import PlatformAI as PAI

class player():
    def __init__(self, x, y, width = 30, height = 50):
        self.rect = pygame.Rect(x, y, width, height)
        self.rect.top = y
        self.rect.left = x
        self.vel = [0,0]
        self.maxvel = 16
        self.maxjump = 36
        self.var = True
        self.health = 10
        self.healthtimer = 0
        self.kills = 0
        self.deaths = 0
        self.alive = True
        self.skulls = pygame.image.load("red-skull.png")
        self.skulls = pygame.transform.scale(self.skulls, (45,45))
        self.skullsurf = pygame.Surface((45,45), SRCALPHA , 32)
        self.skullsurf.blit(self.skulls,(0,0))
        self.skullsurf = self.skullsurf.convert_alpha()
        self.deadtime = 0
        self.zone = None
        self.awareness = 0
        self.weapon = None
        self.firetime = 2
        self.curstreak = 0
        self.killstreak = 0
        self.clip = 0
        self.reloading = False
        self.rank = 0
        self.level = 1
    def reset(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 50)
        self.rect.top = y
        self.rect.left = x
        self.vel = [0,0]
        self.maxvel = 16
        self.maxjump = 36
        self.var = True
        self.health = 10
        self.healthtimer = 0
        self.kills = 0
        self.deaths = 0
        self.alive = True
        self.deadtime = 0
        self.zone = None
        self.awareness = 0
        self.firetime = 2
        self.curstreak = 0
        self.killstreak = 0
        self.reloading = False
    def draw(self, screen, color, walls, xscroll, yscroll, spawnpoints, enemies, truescreen):
        key = pygame.key.get_pressed()
        if (self.clip <=0 or key[K_r]) and not self.reloading and self.clip < self.weapon.magsize:
            self.firetime = self.weapon.reloadtime
            self.reloading = True
        if self.curstreak > self.killstreak:
            self.killstreak = self.curstreak
        self.firetime -=1
        if self.firetime <= 0:
            self.firetime = 0
            if self.reloading:
                self.reloading = False
                self.clip = self.weapon.magsize
        if self.alive:
            if self.health <10:
                self.healthtimer +=1
                if self.healthtimer > 60:
                    self.health += .1
                    if self.health >10:
                        self.health = 10
            onBlock = False
            pygame.draw.rect(screen,color,self.rect)
            mx,my = pygame.mouse.get_pos()
            mx += xscroll
            my += yscroll
            th = math.atan2(my-self.rect.centery,mx-self.rect.centerx)
            img = self.weapon.image
            imw, imh = img.get_size()
            vv = imh/22.0
            img = pygame.transform.scale(img,(int(imw/vv),int(imh/vv)))
            shift = -12
            if (th<math.pi/2 and th>math.pi*-.5) or (th>math.pi*3/2 and th < math.pi*5/2):
                img =pygame.transform.flip(img,False,True)
                shift = 12
            img = pygame.transform.rotate(img, math.degrees(th))
            img = pygame.transform.flip(img,False, True)
            imrec = img.get_rect()
            imrec.centerx = self.rect.centerx + shift
            imrec.centery = self.rect.centery
            screen.blit(img,imrec)

            if self.health <10:
                pygame.draw.rect(screen,(0,255,0),(self.rect.left, self.rect.top - 10, self.health * 3, 4))
            self.vel[1] += 4
            self.rect.y += self.vel[1]
            if self.rect.bottom > 1200:
                self.rect.bottom = 1180
                self.vel[1] = -1
            for i in walls:
                if self.rect.colliderect(i.rect):
                    if self.vel[1]>0:
                        self.rect.bottom=i.rect.top
                    elif self.vel[1]<0:
                        self.rect.top = i.rect.bottom
                    self.vel[1]=0
                if self.rect.bottom == i.rect.top and self.rect.left<i.rect.right and self.rect.right>i.rect.left:
                    onBlock = True
            self.rect.x += self.vel[0]
            for i in walls:
                if self.rect.colliderect(i.rect):
                    if self.vel[0]>0:
                        self.rect.right=i.rect.left
                    elif self.vel[0]<0:
                        self.rect.left = i.rect.right
                    self.vel[0]=0
            k = pygame.key.get_pressed()
            if k[K_RIGHT] or k[K_d]:
                self.vel[0] += 5
                if self.vel[0] > self.maxvel:
                    self.vel[0] = self.maxvel
            if k[K_LEFT] or k[K_a]:
                self.vel[0] -=5
                if self.vel[0] < (-1*self.maxvel):
                    self.vel[0] = (-1*self.maxvel)

            if not k[K_LEFT] and not k[K_RIGHT] and not k[K_a] and not k[K_d]:
                self.vel[0] /= 4.0
                if self.vel[0] < 1 and self.vel[0]>-1:
                    self.vel[0] = 0

            if onBlock:
                if k[K_UP] or k[K_w] or k[K_SPACE]:
                    self.vel[1] = -self.maxjump

            if k[K_t]:
                print self.rect.bottom, self.rect.left, self.rect.right

            if k[K_s] or k[K_DOWN]:
                if self.rect.height==50:
                    self.rect.y+=25
                self.rect.height=25
                self.maxvel=7
                self.maxjump = 28
            else:
                if self.rect.height == 25:
                    self.rect.y -=25
                self.rect.height=50
                self.maxvel=16
                self.maxjump = 36

            if pygame.mouse.get_pressed()[0] and not self.var and self.firetime<=0:
                if not self.weapon.Class == "Full-Auto":
                    self.var = True
                x,y = pygame.mouse.get_pos()
                x += xscroll
                y += yscroll
                self.clip -= 1
                self.firetime = self.weapon.firerate
                if self.zone:
                    if not self.weapon.Class == "Sniper":
                        for e in enemies:
                            e.targets[self.zone] += 9
                            if self.weapon.Class == "Shotgun":
                                e.targets[self.zone] += 4
                ret = [bullet(self.rect.centerx,self.rect.centery,x,y,self)]
                if self.weapon.Class == "Shotgun":
                    for i in range(0,5):
                        ret.append(bullet(self.rect.centerx,self.rect.centery,x,y,self))
                return ret

            if self.var and not pygame.mouse.get_pressed()[0]:
                self.var = False

            poss = None
            for i in PAI.floors:
                if self.rect.bottom <= i.height and self.rect.right > i.left and self.rect.left < i.right:
                    if poss:
                        if i.height < PAI.floors[poss].height:
                            poss = PAI.floors.index(i)
                    else:
                        poss = PAI.floors.index(i)

            self.zone = poss

        else:
            self.rect.y -= 1
            screen.blit(self.skullsurf, self.rect)
            self.deadtime -= 1
            if self.deadtime <=0:
                self.rect.x, self.rect.y = spawnpoints[rand(0, len(spawnpoints) - 1)]
                self.health = 10
                self.clip = self.weapon.magsize
                self.vel = [0,0]
                return True

class bullet():
    def __init__(self, x, y, tx, ty, player):
        self.x = x
        self.y = y
        theta = math.atan2(ty-y,tx-x)
        if player.rect.height >=50:
            theta += rand(-20,20)/float(player.weapon.accuracy)
        else:
            theta += rand(-20,20)/(float(player.weapon.accuracy)*1.5)
        self.vel = [math.cos(theta),math.sin(theta)]

    def draw(self,background,color,walls,enemies,show,player,hvar):
        dead = False
        self.x += 4 * self.vel[0]
        self.y += 4 * self.vel[1]
        if show:
            pygame.draw.circle(background,color,(int(self.x),int(self.y)),1)

        if hvar:
            for enemy in enemies:
                if enemy.rect.collidepoint((int(self.x),int(self.y))):
                    if enemy.alive and enemy.health > 0:
                        dead = True
                        enemy.health -= player.weapon.damage
                        if enemy.health <= 0:

                            player.kills += 1
                            player.curstreak += 1
                        break

            for wall in walls:
                if wall.rect.collidepoint((int(self.x),int(self.y))):
                    dead = True

        if dead:
            return True

class weapon():
    def __init__(self,Class,damage,accuracy,magsize,firerate,reloadtime,name,image,reqlevel,dinc,cost):
        self.reloadtime = reloadtime
        self.firerate = firerate
        self.Class = Class
        self.name = name
        self.image = pygame.image.load(image)
        w = self.image.get_width()
        h = self.image.get_height()
        self.image = pygame.transform.scale(self.image,(w*45/h,45))
        self.damage = damage
        self.accuracy = accuracy
        self.magsize = magsize
        self.reqlevel = reqlevel
        self.var = False
        self.dlvl = 1
        self.dinc = dinc
        self.purchased = False
        self.cost = cost
        self.classlist = ["Semi-Auto","Full-Auto","Shotgun","Sniper"]
    def shopdraw(self,screen, y, width, height, player, cash):
        try:
            font = pygame.font.SysFont('andalemono',25)
        except:
            font = pygame.font.Font(None,35)
        pfont = pygame.font.Font(None,50)
        color = (255,255,255)
        if player.level < self.reqlevel and self.purchased:
            color = (100,100,100)
        nt = font.render(self.name + "    Class: " + self.Class,1,color)
        ntp = nt.get_rect()
        ntp.left = 25
        ntp.top = y
        font = pygame.font.Font(None,25)
        text = "DAMAGE: " + str(self.damage)
        if self.Class == "Shotgun":
            text += " x 5"
        dt = font.render(text, 1, (175,0,0))
        dtp = dt.get_rect()
        dtp.left = width/2
        dtp.top = ntp.bottom
        if self.purchased and self.dlvl <= 3:
            pt = pfont.render("+",1,(255,0,0))
            ptp = pt.get_rect()
            ptp.centery = dtp.centery - 3
            ptp.left = dtp.right + 5
            ptpc = pygame.Rect(ptp.left,ptp.top + 8,ptp.width,ptp.height-13)
            pygame.draw.rect(screen,(0,255,0),ptpc)
            screen.blit(pt,ptp)
            charge = self.dinc *10 *self.dlvl *(1 + self.classlist.index(self.Class))
            if ptpc.collidepoint(pygame.mouse.get_pos()):
                ct = font.render("$"+str(charge),1,(0,255,0))
                ctp = ct.get_rect()
                ctp.centery = ptpc.centery
                ctp.left = ptpc.right + 8
                screen.blit(ct,ctp)
            a,b,c = pygame.mouse.get_pressed()
            if a and not self.var:
                self.var = True
                if ptpc.collidepoint(pygame.mouse.get_pos()) and cash >= charge:
                    cash -= charge
                    self.damage += self.dinc
                    self.dlvl += 1
            if not a and self.var:
                self.var = False

        at = font.render("ACCURACY: " + str(round(100.0*(1-(20.0/self.accuracy)))) + "%",1,(175,0,0))
        atp = at.get_rect()
        atp.left = width/2
        atp.bottom = ntp.bottom + 45
        screen.blit(dt,dtp)
        screen.blit(at,atp)
        screen.blit(nt,ntp)
        rect = self.image.get_rect()
        rect.left = 25
        rect.top = ntp.bottom
        a,b,c = pygame.mouse.get_pressed()
        if a and rect.collidepoint(pygame.mouse.get_pos()) and not self.var and not self.purchased:
            self.var = True
            if cash >= self.cost:
                cash -= self.cost
                self.purchased = True
                player.weapon = self
        if a and rect.collidepoint(pygame.mouse.get_pos()) and self.purchased:
            player.weapon = self

        if not a and self.var:
            self.var = False

        if player.weapon == self:
            pygame.draw.rect(screen,(200,0,0),rect)
        screen.blit(self.image,(25,ntp.bottom))
        surf = pygame.Surface((rect.width,rect.height))
        surf.fill((0,0,0))
        surf.set_alpha(140)
        if player.level < self.reqlevel:
            screen.blit(surf,rect)
            rt = font.render("LEVEL " + str(self.reqlevel),1,(255,0,0))
            rtp = rt.get_rect()
            rtp.left = rect.right + 10
            rtp.centery = rect.centery
            screen.blit(rt,rtp)
        if self.purchased == False and player.level >= self.reqlevel:
            bt = font.render("$"+str(self.cost),1,(0,255,0))
            btp = bt.get_rect()
            btp.left = rect.right + 10
            btp.centery = rect.centery
            screen.blit(bt,btp)

        return ntp.bottom + 55, cash
