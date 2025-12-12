#!/usr/bin/fish
set CPU_TYPE minor o3
set BPRED_TYPE local bimode tournament tage
set ISSUE_WIDTH 1 4 8
echo "Running Tests"
for CPU in $CPU_TYPE
  for BPRED in $BPRED_TYPE
    if test $CPU = "o3"
      for WIDTH in $ISSUE_WIDTH
        ./build/ALL/gem5.opt configs/project/project.py --cpu $CPU --bpred $BPRED --width $WIDTH --bin matrix-multiply
        cp m5out/stats.txt configs/project/data/$CPU-$BPRED-$WIDTH.txt
      end
    end
    if test $CPU = "minor"
      ./build/ALL/gem5.opt configs/project/project.py --cpu $CPU --bpred $BPRED --bin matrix-multiply
      cp m5out/stats.txt configs/project/data/$CPU-$BPRED.txt
    end
  end
end
echo "Data can be found at configs/project/data"
