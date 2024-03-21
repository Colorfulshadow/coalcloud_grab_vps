from grab import grab_vps

def test():
    vps = grab_vps('89','monthly') # annually quarterly or monthly
    while not vps.grab():
        pass
    print("恭喜你！抢到啦，请及时支付哦~")

if __name__ == '__main__':
    test()