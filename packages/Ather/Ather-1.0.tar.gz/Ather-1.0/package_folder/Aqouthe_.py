
def login_and_signup() :
    count = 0
    def sign_up(id, password) :
        nonlocal count
        count = count + 1
        globals()['num_{}'.format(count)] = {}
        globals()['num_{}'.format(count)]['id'] = id
        globals()['num_{}'.format(count)]['password'] = password
    def login(id, password) :
        pass
    




def a() :
    def say_hello(name) :
        print('%s님 안녕하세요' % name)

    say_hello('홍지수')
    say_hello('안지영')
    say_hello('황예린')

def b() :
    def sum(start, end) :
        hap = 0
        for i in range(start, end+1) :
            hap = hap + i
        print('%d ~ %d의 정수의 합계 : %d' %(start, end, hap))
    
    sum(1, 10)
    sum(100, 200)
    sum(200, 300)

def c() :
    def inch_change_cm(inch) :
        cm = inch * 2.54
        return cm
    
    num = int(input('인치 입력하세요 : '))
    result = inch_change_cm(num)
    print('%d inch => %.2f cm' % (num, result))

def d() :
    def fvbesu(num) :
        if num % 5 == 0 :
            s = True
        else :
            s = False
        return s
    
    d = int(input('정수를 입력하세요 : '))
    if fvbesu(d) == True :
        print('%d => 5의 배수이다.' % d)
    else :
        print('%d => 5의 배수가 아니다.' % d)

def e() :
    def sum_besu3(n) :
        sum = 0 
        for i in range(1, n) :
            if i % 3 == 0 :
                sum = sum + i
        
        return sum
    
    b = int(input('양의 정수를 입력하세요. : '))
    print('1~%d 까지의 3의 배수의 합 : %d' % (b ,sum_besu3(b)))

def f() :
    def cir_area(radius) :
        return radius * radius * 3.141592629
    def cir_circum(radius) :
        return 2 * 3.141592629 * radius
    
    f = float(input('반지름을 입력하세요. : '))
    print('원의 면적 : %.9f...  원주의 길이 : %.9f...' % (cir_area(f), cir_circum(f)))

def g() :
    def sum(numbers) :
        sum = 0
        for i in range(len(numbers)) :
            sum = sum + numbers(i)
        return sum
    
    num = (7, 12, 38, 24, 25, -7)
    print(num)
    print(sum(num))

def h() :
    def gcd(x, y) :
        if x > y :
            small = y
        else : 
            small = x
        for i in range(1, small + 1) :
            if((x % i == 0) and (y % i == 0)) :
                result = i
        return result
    
    num = int(input('첫번째 수 입력 : '))
    num2 = int(input('두번쨰 수 입력 : '))
    gcd = gcd(num, num2)
    print('%d와 %d의 최대공약수 : %d' % (num, num2, gcd))


    


