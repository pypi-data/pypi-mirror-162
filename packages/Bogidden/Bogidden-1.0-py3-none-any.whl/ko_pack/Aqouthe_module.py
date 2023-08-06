
from random import *


class password_and_palindrome() :
    def is_palindrom() :
        SpecialProject.scripters_thanks('player') 
        def is_palindrom1(s) :
            for i in range(0, int(len(s)/2)) :
                if s[i] != s[len(s)-i-1] :
                    return False

            return True
        string = "rotator"
        if is_palindrom1(string) :
            print('%s is a palindrome.' % string)
        else :
            print('%s is not a palindrome.' % string)

    def stringshift() :
        SpecialProject.scripters_thanks('player')
        def string_shift(string, d, direction) :
            if direction == "left" :
                left_part = string[d:]
                right_part = string[0:d]
            else :
                left_part = string[len(string)-d:]
                right_part = string[0:len(string)-d]
            result = left_part + right_part
            return result

        string = input('input string : ')

        str_left = string_shift(string, 2, 'left')
        str_right = string_shift(string, 3, 'right')

        print('original string : ' + string)
        print('String shifted 2 spaces to the left : ' + str_left)
        print('String shifted 3 spaces to the right : ' + str_right)
    
    def chat_bot(player_name) :
        b = 0
        print('안녕하세요! 저는 %s님의 챗봇입니다!' % player_name)
        name = input('저의 이름을 입력해주세요! : ')
        while True :
            if b >= 1 :
                print('저 삐졌어요!!')
                b + 1
            if b >=  4 :
                print('뭐 이제는 용서해드릴게요 ㅋㅋ')
                b = 0
                continue
            c = input('저에게 명령을 내려보세요! (아무 말이나 해봐, 안녕?) : ')
            if c == '아무 말이나 해봐' :
                chatlist = {1 : '안녕하세요?', 2 : '오늘 날씨가 좋네요.', 3 : '할 말이 딱히 없군요.', 4 : '어쩔티비 ㅋㅋㄹㅃㅃ', 5 : 'ㅋㅋㅋㅋㅋㅋ', 6 : '어쩌라고요'}
                b = randint(1, 6)
                print(chatlist[b])
            if c == '안녕?' :
                print('안녕하세요 %s님! ㅎㅎ' % player_name)
            
            if c == '어쩌라고' :
                print('왜 그렇게 말하세요!!!!(삐짐)')
                b = b + 1
            else :
                print('무슨 뜻인지 모르겠어요 ㅠㅠ')

        

class SpecialProject() :
    def scripters_thanks(player_name) :
        print('thanks for playing player %s. -Aqouthe' % player_name)




