class normalFraction:
    def __init__(self, numerator, denominator):
        self.nr = numerator
        self.dr = denominator
    def show(self):
        print(f'{self.nr}/{self.dr}')

class mixedFraction:
    def __init__(self, whole, numerator, denominator):
        self.nr = numerator
        self.dr = denominator
        self.w = whole
    def show(self):
        print(f'{self.w} {self.nr}/{self.dr}')

#SIDE FUNCTIONS (REQUIRED FOR THE MAIN FUNCTIONS TO WORK)
def swap(a, b):
    temp = a
    a = b
    b = temp
    return a, b
def hcf(d1, d2):
    i = 1
    while i <= d1 and i <= d2:
        if d1%i == 0 and d2%i == 0:
            hcf_val = i
        i = i + 1
    return hcf_val
def lcm(d1, d2):
    hcf_val = hcf(d1, d2)
    product = d1 * d2
    lcm_val = product/hcf_val
    return int(lcm_val)

#MAIN FUNCTIONS
def simplification(frac):
    i = 2
    while (i <= frac.nr and i <= frac.dr): 
        while (frac.nr%i == 0 and frac.dr%i == 0):
            frac.nr = frac.nr / i
            frac.dr = frac.dr / i
        i = i + 1
    return (normalFraction(int(frac.nr), int(frac.dr)))
def addition(frac1, frac2):
    new_dr = lcm(frac1.dr, frac2.dr)
    new_nr = ((new_dr/frac1.dr) * frac1.nr)+((new_dr/frac2.dr) * frac2.nr)
    return simplification(normalFraction(int(new_nr), new_dr))
def subtraction(frac1, frac2):
    new_dr = lcm(frac1.dr, frac2.dr)
    new_nr = ((new_dr/frac1.dr) * frac1.nr)-((new_dr/frac2.dr) * frac2.nr)
    return simplification(normalFraction(int(new_nr), new_dr))
def multiplication(frac1, frac2):
    new_nr = frac1.nr * frac2.nr
    new_dr = frac1.dr * frac2.dr
    return simplification(normalFraction(new_nr, new_dr))
def division(frac1, frac2):
    frac2.nr, frac2.dr = swap(frac2.nr, frac2.dr) 
    return multiplication(frac1, frac2)
def mixedfraction_to_normal(frac):
    frac.nr = (frac.w * frac.dr) + frac.nr
    return simplification(normalFraction(frac.nr, frac.dr))
def normalfraction_to_mixed(frac):
    whole = int(frac.nr  /frac.dr)
    numerator = frac.nr % frac.dr
    denominator = frac.dr
    return mixedFraction(whole, numerator, denominator)
def mixedfraction_to_decimal(frac):
    normal = mixedfraction_to_normal(frac)
    return normal.nr/normal.dr
def normalfraction_to_decimal(frac):
    return frac.nr/frac.dr
def decimal_to_normalfraction(num, number_of_decimalpoints):
    dr = 1
    for i in range (number_of_decimalpoints):
        num = num * 10
        dr = dr * 10
    return simplification(normalFraction(num, dr))
def decimal_to_mixedfraction(num, number_of_decimalpoints):
    normal = decimal_to_normalfraction(num, number_of_decimalpoints)
    return normalfraction_to_mixed(normal)
def comparison(frac1, frac2):
    
    num1 = frac1.nr/frac1.dr
    num2 = frac2.nr/frac2.dr
    if num1>num2:
        return 1
    else:
        return 0