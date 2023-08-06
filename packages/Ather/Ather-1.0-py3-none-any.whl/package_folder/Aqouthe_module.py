
class fuction() :
    def args_parameter() :
        SpecialProject.scripters_thanks
        def average(*args) :
            num_args = len(args)
            sum = 0
            for i in range(num_args) :
                sum = sum + args[i]
            avg = sum/num_args
            print('%d과목 평균 : %.1f' %(num_args, avg))
        average(85, 96, 87)
        average(77, 93, 85, 97, 72)

    def send_list_for_paremeter() :
        SpecialProject.scripters_thanks()
        def func(food) :
            for x in food :
                print(x)
        fruit = ["사과", "오랜지", "바나나"] 
        func(fruit)

    def is_palindrom() :
        SpecialProject.scripters_thanks('dev') 
        def is_palindrom1(s) :
            for i in range(0, int(len(s)/2)) :
                if s[i] != s[len(s)-i-1] :
                    return False

            return True
        string = "rotator"
        if is_palindrom1(string) :
            print('%s는 회문이다!' % string)
        else :
            print('%s는 회문이 아니다!' % string)

    def stringshift() :
        def string_shift(string, d, direction) :
            if direction == "left" :
                left_part = string[d:]
                right_part = string[0:d]
            else :
                left_part = string[len(string)-d:]
                right_part = string[0:len(string)-d]
            result = left_part + right_part
            return result

        string = 'pythonprogramming'

        str_left = string_shift(string, 2, 'left')
        str_right = string_shift(string, 3, 'right')

        print('원래 문자열 : ' + string)
        print('좌측으로 2칸 이동 : ' + str_left)
        print('우측으로 3칸 이동 : ' + str_right)
        

class SpecialProject() :
    def scripters_thanks(player_name) :
        print('thanks for playing player %s. -Aqouthe_' % player_name)




