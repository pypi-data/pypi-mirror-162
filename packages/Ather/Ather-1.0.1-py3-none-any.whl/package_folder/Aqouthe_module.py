
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
        

class SpecialProject() :
    def scripters_thanks(player_name) :
        print('thanks for playing player %s. -Aqouthe' % player_name)




