def make_final_timeline(laughter_timeline,person_timeline,max_length=None):
    p_timeline = person_timeline.copy()
    final = []
    total_length = 0
    for ind,(start,end,laugh_len,laugh_db) in enumerate(laughter_timeline):
        shot_length = end-start
        length=0
        while p_timeline:
            s,e = p_timeline.pop(0)
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
                person_interest = (length/shot_length - 0.3)/0.4
                total_interest = laugh_len*3 + laugh_db*2 + person_interest*1
                final.append((round(start-5,2),end,round(total_interest,2),round(length/shot_length,3), shot_length))
                total_length += shot_length
        else:
            if length/shot_length > 0.30:
                person_interest = (length/shot_length - 0.3)/0.4
                total_interest = laugh_len*3 + laugh_db*2 + person_interest*1
                final.append((round(start-5,2),end,round(total_interest,2),round(length/shot_length,3), shot_length))
                total_length += shot_length  
            
    # max_length 넘어가는 경우 흥미도 높은 순서로 max_length 이내로 선택
    if max_length and total_length > max_length:
        sorted_timeline = sorted(final,key=lambda x:-x[2])
        choose_index = [False for _ in range(len(sorted_timeline))]
        total_length = 0
        for start,end,interest,ratio, duration in sorted_timeline:
            length = end - start
            if total_length + length > max_length:
                break
            else:
                total_length += length
                choose_index[final.index((start,end,interest,ratio,duration))] = True
                
        new_final = []
        for ind, (s,e,i,r,d) in enumerate(final):
            if choose_index[ind]:
                new_final.append((s,e,i,r,d))
        final = new_final
    
    # interest 순서로 정렬
    final.sort(key=lambda x:-x[2])
    return final, round(total_length,2)