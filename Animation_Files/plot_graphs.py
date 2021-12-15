from matplotlib import pyplot as plt
import numpy as np

plt.figure(dpi=1000, figsize=(6,8))

plt.bar(["Local M/C", "Discovery"], [1174, 515], color=["tomato", "orange"], width=0.5)
plt.ylabel("Time per Step (s)")

plt.plot(np.linspace(-0.5, 1.5, 100), 30*np.ones(100), "--m", label="Less Ambitious Target")
plt.plot(np.linspace(-0.5, 1.5, 100), 5*np.ones(100), "--",color="lime", label="Ambitious Target")
plt.xlabel("Instance")
plt.ylabel("Time (s)")
plt.title("BASELINE - Rendering w/ 500 Plants")
plt.legend()
plt.tight_layout() 
plt.savefig("assets/timing_results.png")
plt.close()


plt.figure(dpi=1000, figsize=(6,8))
multithreading_results = [510.234, 260.784, 110.0, 62.164, 58.716, 54.624, 54.288, 54.070, 54.044, 55.9]
thread_labels = ["1", "2", "5", "10", "20", "50", "64", "100", "200", "500"]
plt.bar(thread_labels, multithreading_results, align='center')
plt.plot(np.linspace(-0.5, 9.5, 100), 30*np.ones(100), "--", color="magenta", label="Less Ambitious Target")
plt.plot(np.linspace(-0.5, 9.5, 100), 5*np.ones(100), "--",color="lime", label="Ambitious Target")
plt.xlabel("Number of Threads")
plt.ylabel("Time (s)")
plt.title("Multithreaded Rendering", fontsize=14)
plt.legend()
plt.tight_layout() 
plt.savefig("assets/multithreading_results.png")
plt.close()

plt.figure(dpi=1000, figsize=(6,8))
mpi_multithreading_results = [38.530, 20.844, 8.703, 4.858, 4.753, 4.374, 4.358, 4.288, 4.346, 4.424]
thread_labels = ["1", "2", "5", "10", "20", "50", "64", "100", "200", "500"]
plt.bar(thread_labels, mpi_multithreading_results, align='center')
plt.plot(np.linspace(-0.5, 9.5, 100), 30*np.ones(100), "--", color="magenta", label="Less Ambitious Target")
plt.plot(np.linspace(-0.5, 9.5, 100), 5*np.ones(100), "--",color="lime", label="Ambitious Target")
plt.xlabel("Number of Threads")
plt.ylabel("Time (s)")
plt.title("Hybrid MPI (Size = 13) + Multithreaded Rendering", fontsize=14)
plt.legend()
plt.tight_layout() 
plt.savefig("assets/hybrid_mpi_multithreading_results.png")
plt.close()

plt.figure(dpi=1000, figsize=(6,8))
mpi_results = [509.358, 274.225, 157.734, 78.897, 77.913, 38.530]
mpi_labels = ["1", "2", "4", "8", "12", "13"]
plt.bar(mpi_labels, mpi_results, align='center')
plt.plot(np.linspace(-0.5, 5.5, 100), 30*np.ones(100), "--", color="magenta", label="Less Ambitious Target")
plt.plot(np.linspace(-0.5, 5.5, 100), 5*np.ones(100), "--",color="lime", label="Ambitious Target")
plt.xlabel("MPI Size")
plt.ylabel("Time (s)")
plt.title("MPI Rendering", fontsize=14)
plt.legend()
plt.tight_layout() 
plt.savefig("assets/mpi_results.png")
plt.close()