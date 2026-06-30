import pyhepmc
import numpy as np
    
f_name = "test_job.hepmc"

def analyseFile(f_name, nu_PDG, nubar_PDG):
    nu_eta = []
    nubar_eta = []    
    gamma_eta = []

    nu_phi = []
    nubar_phi = []    
    gamma_phi = []

    nu_px = []
    nubar_px = []    
    gamma_px = []

    nu_py = []
    nubar_py = []    
    gamma_py = []

    nu_E = []
    nubar_E = []
    gamma_E = []

    m_Z = []

    with pyhepmc.open(f_name) as f:
        for event in f:
            E = 0
            px = 0
            py = 0
            pz = 0
            for p in event.particles:
                if p.status != 1:
                    continue
                if p.pid == nu_PDG:
                    nu_eta.append(p.momentum.eta())
                    nu_phi.append(p.momentum.phi())
                    nu_E.append(p.momentum.e)
                    nu_px.append(p.momentum.x)
                    nu_py.append(p.momentum.y)
                    E += p.momentum.e
                    px += p.momentum.x
                    py += p.momentum.y
                    pz += p.momentum.z
                elif p.pid == nubar_PDG:
                    nubar_eta.append(p.momentum.eta())
                    nubar_phi.append(p.momentum.phi())
                    nubar_E.append(p.momentum.e)
                    nubar_px.append(p.momentum.x)
                    nubar_py.append(p.momentum.y)
                    E += p.momentum.e
                    px += p.momentum.x
                    py += p.momentum.y
                    pz += p.momentum.z
                elif p.pid == 22:
                    gamma_eta.append(p.momentum.eta())
                    gamma_E.append(p.momentum.e)
                else:
                    raise RuntimeError("Unknown final state particle")
            m_Z.append((E**2 - (px**2 + py**2 + pz**2))**0.5)

    return {"nu_eta": np.array(nu_eta),
            "nubar_eta": np.array(nubar_eta),
            "nu_phi": np.array(nu_phi),
            "nubar_phi": np.array(nubar_phi),
            "nu_px": np.array(nu_px),
            "nubar_px": np.array(nubar_px),
            "nu_py": np.array(nu_py),
            "nubar_py": np.array(nubar_py),
            "nu_E": np.array(nu_E),
            "nubar_E": np.array(nubar_E),
            "gamma_eta": np.array(gamma_eta),
            "m_Z": np.array(m_Z),
            "nu_PDG": nu_PDG,
            "nubar_PDG": nubar_PDG}

d = {}
d["nue"] = analyseFile("test_nue_100k_91.2_ISR_PA/test_nue_100k_91.2_ISR_PA.hepmc", 12, -12)
d["numu"] = analyseFile("test_numu_100k_91.2_ISR_PA/test_numu_100k_91.2_ISR_PA.hepmc", 14, -14)
d["nutau"] = analyseFile("test_nutau_100k_91.2_ISR_PA/test_nutau_100k_91.2_ISR_PA.hepmc", 16, -16)
d["mu"] = analyseFile("test_mu_100k_91.2_ISR_PA/test_mu_100k_91.2_ISR_PA.hepmc", 13, -13)
d["mu_noISR"] = analyseFile("test_mu_100k_91.2_PA/test_mu_100k_91.2_PA.hepmc", 13, -13)

print("Mean eta")
for particle in d.keys():
    print(f"{particle}: {np.mean(d[particle]['nu_eta'])}")
print()
print("AFB")
Afb = {}
eta = {}
etabar = {}
for particle in d.keys():
    eta[particle] = d[particle]['nu_eta']
    etabar[particle] = d[particle]['nubar_eta']
    
    Afb[particle] = (np.sum(eta[particle] > 0) - np.sum(eta[particle] < 0)) / (np.sum(eta[particle] > 0) + np.sum(eta[particle] < 0))
    print(f"{particle}: {Afb[particle]}")

# Afb measurement toys
N_numuplusnumubar = 900.
N_numu = N_numuplusnumubar*2./3
N_numubar = N_numuplusnumubar*1./3

i_nu = 0
i_nubar = 0

Afb_throws_numu = []
Afb_throws_numubar = []

meaneta_throws_numu = []
meaneta_throws_numubar = []

medianeta_throws_numu = []
medianeta_throws_numubar = []
while True:
    N_throw_numu = np.random.poisson(N_numu)
    N_throw_numubar = np.random.poisson(N_numubar)

    if i_nu + N_throw_numu >= len(eta["numu"]):
        break

    eta_throw_numu = eta["numu"][i_nu:i_nu + N_throw_numu]
    eta_throw_numubar = etabar["numu"][i_nubar:i_nubar + N_throw_numubar]
    
    Afb_throws_numu.append((np.sum(eta_throw_numu > 0) - np.sum(eta_throw_numu < 0)) / (np.sum(eta_throw_numu > 0) + np.sum(eta_throw_numu < 0)))
    Afb_throws_numubar.append((np.sum(eta_throw_numubar > 0) - np.sum(eta_throw_numubar < 0)) / (np.sum(eta_throw_numubar > 0) + np.sum(eta_throw_numubar < 0)))

    meaneta_throws_numu.append(np.mean(eta_throw_numu))
    meaneta_throws_numubar.append(np.mean(eta_throw_numubar))

    medianeta_throws_numu.append(np.median(eta_throw_numu))
    medianeta_throws_numubar.append(np.median(eta_throw_numubar))

    i_nu += N_throw_numu
    i_nubar += N_throw_numubar

    
import matplotlib.pyplot as plt

plt.figure()
plt.hist(Afb_throws_numu, range = (-0.3, 0.3), bins = 30, label = r"$\nu_\mu$")
plt.hist(Afb_throws_numubar, range = (-0.3, 0.3), bins = 30, label = r"$\bar{\nu}_\mu$")

afb_var_numu = np.var(Afb_throws_numu)
afb_var_numubar = np.var(Afb_throws_numubar)

afb_combination = np.add(np.multiply(afb_var_numubar,Afb_throws_numu), np.multiply(-1*afb_var_numu,Afb_throws_numubar))/(afb_var_numu+afb_var_numubar)

print(f"Number of toys: {len(Afb_throws_numu)}")
print(f"Combined statistical uncertainty on Afb {np.std(afb_combination)/np.mean(afb_combination):.3f}")
plt.hist(afb_combination, range = (-0.3, 0.3), bins = 30, label = r"$\nu_\mu+\bar{\nu}_\mu$", histtype = "step")

plt.legend()
plt.xlabel(r"$A_{FB}$")
plt.ylabel("Number of toys")

plt.figure()
plt.hist(meaneta_throws_numu, range = (-0.3, 0.3), bins = 30, label = r"$\nu_\mu$")
plt.hist(meaneta_throws_numubar, range = (-0.3, 0.3), bins = 30, label = r"$\bar{\nu}_\mu$")
meaneta_var_numu = np.var(meaneta_throws_numu)
meaneta_var_numubar = np.var(meaneta_throws_numubar)
meaneta_combination = np.add(np.multiply(meaneta_var_numubar, meaneta_throws_numu), np.multiply(-1*meaneta_var_numu, meaneta_throws_numubar))/(meaneta_var_numu+meaneta_var_numubar)
plt.hist(meaneta_combination, range = (-0.3, 0.3), bins = 30, label = r"$\nu_\mu+\bar{\nu}_\mu$", histtype = "step")
plt.legend()
plt.xlabel(r"$< \eta >$")
plt.ylabel("Number of toys")

print(f"Combined statistical uncertainty on mean eta {np.std(meaneta_combination)/np.mean(meaneta_combination):.3f}")

plt.figure()
plt.hist(medianeta_throws_numu, range = (-0.3, 0.3), bins = 30, label = r"$\nu_\mu$")
plt.hist(medianeta_throws_numubar, range = (-0.3, 0.3), bins = 30, label = r"$\bar{\nu}_\mu$")
medianeta_var_numu = np.var(medianeta_throws_numu)
medianeta_var_numubar = np.var(medianeta_throws_numubar)
medianeta_combination = np.add(np.multiply(medianeta_var_numubar, medianeta_throws_numu), np.multiply(-1*medianeta_var_numu, medianeta_throws_numubar))/(medianeta_var_numu+medianeta_var_numubar)
plt.hist(medianeta_combination, range = (-0.3, 0.3), bins = 30, label = r"$\nu_\mu+\bar{\nu}_\mu$", histtype = "step")
plt.legend()
plt.xlabel(r"Median $\eta$")
plt.ylabel("Number of toys")

print(f"Combined statistical uncertainty on median eta {np.std(medianeta_combination)/np.mean(medianeta_combination):.3f}")

label_dict = {12: r"$\nu_e$",
              -12: r"$\bar{\nu}_e$",
              14: r"$\nu_\mu$",
              -14: r"$\bar{\nu}_\mu$",
              16: r"$\nu_\tau$",
              -16: r"$\bar{\nu}_\tau$",
              11: r"$e^-$",
              -11: r"$e^+$",
              13: r"$\mu^-$",
              -13: r"$\mu^+$"}

plt.figure()
for i_particle, particle in enumerate(d.keys()):
    plt.hist(d[particle]["nu_eta"], bins = 100, range = (-5, 5), histtype = "step", label = label_dict[d[particle]["nu_PDG"]], color = f"C{i_particle}")
    plt.hist(d[particle]["nubar_eta"], bins = 100, range = (-5, 5), histtype = "step", label = label_dict[d[particle]["nubar_PDG"]], color = f"C{i_particle}", linestyle = ":")
plt.legend()
plt.xlabel(r"$\eta$")

plt.figure()
for i_particle, particle in enumerate(d.keys()):
    plt.hist(d[particle]["nu_phi"], bins = 100, range = (-5, 5), histtype = "step", label = label_dict[d[particle]["nu_PDG"]], color = f"C{i_particle}")
    plt.hist(d[particle]["nubar_phi"], bins = 100, range = (-5, 5), histtype = "step", label = label_dict[d[particle]["nubar_PDG"]], color = f"C{i_particle}", linestyle = ":")
plt.legend()
plt.xlabel(r"$\phi$")

plt.figure()
for i_particle, particle in enumerate(d.keys()):
    plt.hist(d[particle]["nu_E"], bins = 100, range = (30, 60), histtype = "step", label = label_dict[d[particle]["nu_PDG"]], color = f"C{i_particle}")
    plt.hist(d[particle]["nubar_E"], bins = 100, range = (30, 60), histtype = "step", label = label_dict[d[particle]["nubar_PDG"]], color = f"C{i_particle}", linestyle = ":")
plt.legend()
plt.xlabel(r"Energy [GeV]")

plt.figure()
for i_particle, particle in enumerate(d.keys()):
    plt.hist(d[particle]["nu_px"], bins = 100, range = (-50, 50), histtype = "step", label = label_dict[d[particle]["nu_PDG"]], color = f"C{i_particle}")
    plt.hist(d[particle]["nubar_px"], bins = 100, range = (-50, 50), histtype = "step", label = label_dict[d[particle]["nubar_PDG"]], color = f"C{i_particle}", linestyle = ":")
plt.legend()
plt.xlabel(r"p$_x$ [GeV]")

plt.figure()
for i_particle, particle in enumerate(d.keys()):
    plt.hist(d[particle]["nu_py"], bins = 100, range = (-50, 50), histtype = "step", label = label_dict[d[particle]["nu_PDG"]], color = f"C{i_particle}")
    plt.hist(d[particle]["nubar_py"], bins = 100, range = (-50, 50), histtype = "step", label = label_dict[d[particle]["nubar_PDG"]], color = f"C{i_particle}", linestyle = ":")
plt.legend()
plt.xlabel(r"p$_y$ [GeV]")

plt.figure()
for i_particle, particle in enumerate(d.keys()):
    plt.hist(np.add(d[particle]["nu_px"],d[particle]["nubar_px"]), bins = 100, range = (-1, 1), histtype = "step", label = label_dict[d[particle]["nu_PDG"]], color = f"C{i_particle}")
plt.legend()
plt.xlabel(r"$\Sigma$ p$_x$ [GeV]")

plt.figure()
for i_particle, particle in enumerate(d.keys()):
    plt.hist(np.add(d[particle]["nu_py"],d[particle]["nubar_py"]), bins = 100, range = (-1, 1), histtype = "step", label = label_dict[d[particle]["nu_PDG"]], color = f"C{i_particle}")
plt.legend()
plt.xlabel(r"$\Sigma$ p$_y$ [GeV]")


plt.show()
