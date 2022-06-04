cloth_weight=(1.0 0.5 0.6 0.7 0.8 0.9 1.0)
sim_thresh=(0.63 0.64 0.66 0.68 0.70 0.72)
face_cnt=(250 330 350 380 410 440 470 500)
min_csize=(10 8 10 15)
use_merging=(true false)

for sim in "${sim_thresh[@]}"; do
    for face in "${face_cnt[@]}"; do
        for csize in "${min_csize[@]}"; do
            for merge in "${use_merging[@]}"; do
                for cloth_w in "${cloth_weight[@]}"; do
                    python extract_persons.py --weights 1.0 ${cloth_w} --sim-thresh ${sim} --face-cnt ${face} --min-csize ${csize} --use-merging ${merge}
                    echo "[EXP] sim_thresh=${sim} face_cnt=${face} min_csize=${csize} use_merging=${merge} weights=1.0 ${cloth_w}"
                done
            done
        done
    done
done
