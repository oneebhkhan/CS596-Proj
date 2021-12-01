from matplotlib import pyplot as plt
import numpy as np

plt.figure(dpi=60, figsize=(5,8))

plt.bar(["Local M/C", "Discovery"], [1174, 515], color=["tomato", "orange"])
plt.ylabel("Time per Step (s)")

plt.plot(np.linspace(0, 2, 100), 30*np.ones(100), "--m", label="Less Ambitious Target")
plt.plot(np.linspace(0, 2, 100), 5*np.ones(100), "--",color="lime", label="Ambitious Target")
plt.xlabel("Instance")
plt.title("BASELINE - Rendering w/ 500 Plants")
plt.legend()
plt.tight_layout() 
plt.savefig("timing_results.png")
plt.close()