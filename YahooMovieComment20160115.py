# -*- coding: utf-8 -*-  
import pypyodbc as pyodbc  
import urllib.request, urllib.parse, urllib.error
import math
import ssl

"""手動輸入變數"""
#將page設為全域變數，評價總頁數，並給定初值確保可以執行第一遍得到準確頁數
global page
pages=1

#令一變數isIDF，為電影範圍的頭
global isIDnumF
isIDnumF=6042

global movieName
movieName = "第5毀滅"
global movieID
movieID = 108

"""手動輸入變數"""

#令一變數isIDE，為電影範圍的尾
global isIDnumE
isIDnumE=isIDnumF+1
#將isPage設為全域變數，用此判斷是否已經得到頁數
global isPage
isPage=0

#將check設為全域變數，用此判斷是否此行為評價
global check
check=0

#將isUser設為全域變數，用此判斷是否此行為發表人
global isUser
isUser=0
#將counter設為全域變數，為評價數量的計數器
global counter
counter=1
#資料庫變數
global movieDate
movieDate = "null"
global movieAuthor
movieAuthor = "null"
global commentData
commentData = "null"

#辭庫比對變數
global opinionDictionary
opinionDictionary={}
global singleCommentScore
singleCommentScore=0
global finalSingleCommentScore
finalSingleCommentScore=0
global amountOfOpinionMatch
amountOfOpinionMatch=0
global finalTotalCommentScore
finalTotalCommentScore=0
#使用HTMLParser
import html.parser  
  
# 用來解析yahoo電影評價的解析器，繼承自HTMLParser  
class movieHTMLParser(html.parser.HTMLParser):
    
    def handle_starttag(self, tag, attrs):
        global check


    #用來抓標籤外的資料(即評分內容)
    def handle_data(self, data):
        global check
        global isPage
        global page
        global isUser
        global movieDate
        global movieAuthor
        global commentData
        global opinionDictionary
        global singleCommentScore
        global finalSingleCommentScore
        global amountOfOpinionMatch
        global finalTotalCommentScore
        global movieName
        global movieID
        #若發現此行內容為"評分："，為一段評分的start
        if data=='評分：':

            #印出第幾筆
            global counter
            counter+=1
            #將全域變數check設為1，代表接下來的皆為評價
            check=1

        #依觀察，若出現'共'且還未計算過頁數，則下一筆為總筆數
        if data=='共'and isPage==0:
            #將check設為2，代表下一筆為總筆數
            check=2
            
        #若發現此行內容為"你覺得這項短評有幫助嗎？ [ "，為一段評分的end
        elif data=='你覺得這項短評有幫助嗎？ [ ':
            #將全域變數check設為0，代表此段評價結束
            #print u'"\n'
            check=0
            
        #若此行為評價，且是有內容，不為空白格，印出
        if check==1 and data.isspace()==0 and data!='評分：':
            #print data[0:5]
            if data[0:4]=='發表人：':
                isUser=1
                #print u'%s' % data[4:]
                movieAuthor=data[4:]
            elif data[0:5]=='發表時間：':
                isUser=0
                #print u'%s' % data[5:]
                movieDate=data[5:]
            elif data[0:3]=='標題：':
                #print u'%s\n' % data[3:]
                forchange=0
            else :
                if data=='上一頁':
                    check=2
                else:
                    #print u'%s' % data
                    data.replace("你已經給予過推薦了", "")
                    #fout.writelines('%s ' % data +"@#@#%&%&")
                    #fout.writelines('\n')
                    
                    #將評論匯入資料庫
                    commentData=data
                    cursor.execute("INSERT into Comment VALUES (?, ?, ?, ?, ?, ?, ?)", (movieID, movieName, counter-1, movieDate, movieAuthor, commentData, 2))
                    conn.commit()
                    #print("Comment:",commentData)
                    #利用辭庫比對評論計算分數
                    for words in opinionDictionary.items():
                    #words[0]是意見 words[1]是分數
                        #print(words[0],words[1])
                        if words[0] in data:
                            #某一則評論總成績
                            singleCommentScore += int(words[1])
                            amountOfOpinionMatch = amountOfOpinionMatch + 1
                        
                            #print ("get the word:",words[0],"in comment:",movieAuthor,"score:",words[1],"目前累積",singleCommentScore )
                    if (singleCommentScore > 0) :
                        #個別評論總分加總 + = 某評論的總分/對到的意見詞數量
                        finalSingleCommentScore += (singleCommentScore / amountOfOpinionMatch);
                        #print("該作者給的總分:",finalSingleCommentScore)
                        finalTotalCommentScore+=finalSingleCommentScore
                        #print("所有作者累積總分:",finalTotalCommentScore)
                    
                
                      
                #初始
                singleCommentScore=0
                amountOfOpinionMatch=0
                finalSingleCommentScore=0
                

        #若下一筆為總筆數，且確定為整數，計算頁數
        elif check==2 and data.isdigit()==1:

            #總筆數/每頁筆數，並透過ceil方法無條件進位，存進tmp
            tmp=math.ceil(float(data)/10)

            #將型態為浮點數的tmp轉成int存進page
            page=int(tmp)
            print(page,'@@')
            #因為筆數資料是出現在評價之前，所以把check設回1，以利之後計算
            check=0
            #把isPage設為1，代表已經找過頁數，之後不需在尋找
            isPage=1

        
  
    def unknown_decl(self, data):
        global check
        if check==1:
            """Override unknown handle method to avoid exception"""  
        pass


for y in range(isIDnumF,isIDnumE):
    
    #用迴圈來跑頁數
    for x in range(pages):
        print(("up to page:"+str(x+1)))
        # 抓取Yahoo!電影的網頁內容放到WebContent
        url="http://tw.movie.yahoo.com/movieinfo_review.html/id=" + str(y) + "&s=0&o=0&p=" + str(x+1)
        # SSL驗證問題  (update in 2016/1/22)
        context = ssl._create_unverified_context()
        movieWeb = urllib.request.urlopen(url, context=context)
        webContent = movieWeb.read().decode('utf_8')  
        movieWeb.close()

        try:
            # 連結資料庫
            conn = pyodbc.connect('DRIVER={SQL Server};SERVER=YourIPAdress;DATABASE=YouTube;UID=id;PWD=password')
            cursor = conn.cursor()
            #print("----------連結資料庫成功----------")
            #利用辭庫建立字典
            cursor.execute("SELECT * FROM dbo.Thesaurus")
            rows = cursor.fetchall()
            opinionDictionary={}
            #dict({"id": 0,"opinion": '意見',"scores": '分數'})
            #計算辭庫筆數
            count = 0 
            for opinion in rows:
                count = count + 1
                #開始建立字典
                opinionDictionary[opinion[0]] = opinion[1]

            #確認全部字典   
            #print (opinionDictionary.values())



        except IOError as xxx_todo_changeme:
            (errno, strerror) = xxx_todo_changeme.args
            print("I/O error(%s): %s" % (errno, strerror))
  
        Parser = movieHTMLParser()  
  
        try:  
            # 將網頁內容拆成一行一行餵給Parser  
            for line in webContent.splitlines():  
                Parser.feed(line)  
        except html.parser.HTMLParseError as data:  
            print("# Parser error : " + data.msg)  
  
        Parser.close()
#print("----------Star連結資料庫成功----------")        
 # 連結資料庫
conn = pyodbc.connect('DRIVER={SQL Server};SERVER=YourIPAdress;DATABASE=YouTube;UID=id;PWD=password')
cursor = conn.cursor()
cursor.execute("INSERT into Star VALUES (?, ?, ?, ?)", (movieID, movieName,int(finalTotalCommentScore/(counter-1)),2))
conn.commit()
conn.close()

#print("目前電影總分:",finalTotalCommentScore/(counter-1))

print("----------資料匯入成功----------")
 
