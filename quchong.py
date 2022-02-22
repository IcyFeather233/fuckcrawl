list01 = []
for i in open('doc/全唐诗+全宋诗.txt', encoding="utf-8"):
    if i in list01:
        continue
    list01.append(i)
with open('doc/去重全唐诗+全宋词.txt', 'w', encoding="utf-8") as handle:
    handle.writelines(list01)