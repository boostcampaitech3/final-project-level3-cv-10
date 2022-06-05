def make_final_timeline(laughter_timeline,person_timeline,max_length=None):
    p_timeline = person_timeline.copy()
    final = []
    total_length = 0
    for ind,[start,end,interest] in enumerate(laughter_timeline):
        shot_length = end-start
        length=0
        while p_timeline:
            s, e = p_timeline.pop(0)
            if e<start:
                continue
            if s>end:
                p_timeline.insert(0,(s,e))
                break
            s = max(s,start)
            e = min(e,end)
            length += (e-s)
        if shot_length < 35:
            if length/shot_length > 0.35:
                final.append((start,end,interest,shot_length))
                total_length += shot_length
        else:
            if length/shot_length > 0.30:
                final.append((start,end,interest,shot_length))
                total_length += shot_length  
            
    # max_length 넘어가는 경우 등장비율 높은 순서로 max_length 이내로 선택
    if max_length and total_length > max_length:
        sorted_timeline = sorted(final,key=lambda x:-x[3])
        choose_index = [False for _ in range(len(sorted_timeline))]
        total_length = 0
        for start,end,ratio,interest in sorted_timeline:
            length = end - start
            if total_length + length > max_length:
                break
            else:
                total_length += length
                choose_index[final.index((start,end,ratio,interest))] = True
                
        new_final = []
        for ind, (s,e,r,i) in enumerate(final):
            if choose_index[ind]:
                new_final.append((s,e,r,i))
        final = new_final
    
    # interest 순서로 정렬
    final.sort(key=lambda x:-x[2])
    return final, round(total_length,2)