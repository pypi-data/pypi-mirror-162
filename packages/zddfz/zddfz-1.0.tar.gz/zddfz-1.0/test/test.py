s = "aeiou"
k = 2
class lee:
    if __name__ == '__main__':
        left = 0
        right = 0
        maxnum = 0
        amax = 0
        st = ['a','e','i','o','u']
        while right < len(s):
            if s[right] in st:
                maxnum += 1
            right += 1
            if right >= k:
                amax = max(maxnum,amax)
                if s[left] in st:
                    maxnum -= 1
                left += 1

        print(amax)
