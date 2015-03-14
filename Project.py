from bs4 import BeautifulSoup
import urllib2
import pynotify
import datetime

class Sport:
    def __init__(self,site):
        self.site=site

    def parsePage(self):
        pass
                
class Cricket(Sport):
    def __init__(self, site):
        Sport.__init__(self, site)
        self.parsePage()
        self.teams = []
        self.image = "cricket.jpg"
        self.title = "Cricket Update"

    def currInn(self, inn1, inn2):
        if '(' in inn2:
            return inn2
        else:
            return inn1

    def getWickets(self, inn):
        wickets = 0
        if '/' in inn:
            for digit in inn[inn.index('/')+1:]:
                if digit == ' ':
                    return wickets
                else:
                    wickets = wickets*10 + (ord(digit)-48)
        else:
            return 0
        
    def parsePage(self):
        self.inningsL1 = []
        self.inningsL2 = []
        self.currInnings = []
        self.match_status = []
        response= urllib2.urlopen(self.site)
        html = response.read()

        parsed_html = BeautifulSoup(html)
        x = parsed_html.body.find('section', attrs={'class':'matches-day-block'})

        matchList = x.find_all('section', attrs={'class':'default-match-block'})

        for match in matchList:
                inn1 = match.find('div', attrs={'class':'innings-info-1'}).text
                inn2 = match.find('div', attrs={'class':'innings-info-2'}).text
                status = match.find('div',attrs={'class':'match-status'}).text
                self.inningsL1.append(inn1)
                self.inningsL2.append(inn2)
                self.match_status.append(status)
                self.currInnings.append(self.currInn(inn1, inn2))
        
    def set_prefs(self,teams):
        new_teams=[]
        for team in teams:
            new_teams.append(team[:3])
        self.teams= self.teams + new_teams
        
    def scoreString(self, wicket=0):
        score = ""
        for i in range(len(self.inningsL1)):
            if( self.inningsL1[i][1:4] in self.teams or self.inningsL2[i][1:4] in self.teams):
                if (wicket == 1 and not self.getWickets(self.currInn(self.inningsL1[i], self.inningsL2[i])) == self.wicketList[i]) or wicket == 0:
                 score += self.inningsL1[i]
                 score += self.inningsL2[i]
                 score += self.match_status[i]
        return score

    def updateWickets(self):
        self.wicketList = []
        for index in range(0, len(self.inningsL1)):
            self.wicketList.append(0)
        for index in range(0, len(self.inningsL1)):
            self.wicketList[index] = self.getWickets(self.currInn(self.inningsL1[index], self.inningsL2[index]))
           

def send_message(title, scoreString):
    pynotify.init("image")
    notice = pynotify.Notification(title, scoreString, "cricket.jpg").show()
    return notice

cricketGame=Cricket('http://www.espncricinfo.com/ci/engine/match/index.html?view=live')                          
cricketGame.set_prefs(['India','Pakistan'])

timeOld = datetime.datetime.now().replace(microsecond=0)
cricketGame.parsePage()
cricketGame.updateWickets()

while(True):
    timeNew = datetime.datetime.now().replace(microsecond=0)
    diff = timeNew - timeOld
    hours = (diff.seconds)/3600
    minutes= (diff.seconds - hours*3600)/60
    seconds = (diff.seconds - (hours*3600 + minutes*60))
    cricketGame.parsePage()
    
    if seconds > 30:
        send_message(cricketGame.title, cricketGame.scoreString())
        timeOld = timeNew
    else:
        for i in range(len(cricketGame.inningsL1)):
            if not cricketGame.getWickets(cricketGame.currInn(cricketGame.inningsL1[i], cricketGame.inningsL2[i])) == cricketGame.wicketList[i]:
                send_message("WICKET!", cricketGame.scoreString(1))
                timeOld = timeNew

    cricketGame.updateWickets()
    
        





