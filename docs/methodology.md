# Analytical Methodology & Core Definitions

## 1. Core Research Question

> **How does a listener's musical taste actually develop over time?**

Standard annual retrospectives (e.g., Spotify Wrapped) compute simple static sums (Top Artists, Top Songs, Total Minutes). They fail to answer:
1. What triggers long-term interest in an artist's discography?
2. Which songs serve as discovery gateways vs isolated one-time listens?
3. How do albums and EPs actually get explored?
4. How do music networks evolve over years?

---

## 2. Non-Negotiable Analytical Rules

### A. The $\ge 3$-Track Project Exploration Rule
A project (Album/EP) qualifies as **"Explored"** when:
$$\text{Unique Tracks Heard} \ge 3$$
- **Rationale**: Many modern EPs comprise exactly 3 tracks. Setting the threshold to 4 would misclassify completely listened EPs as unexplored.
- **Exploration vs Penetration**:
  - A 3-track EP with 3 tracks heard = 100% complete.
  - A 20-track album with 3 tracks heard = Explored, but with 15% penetration.

### B. Sessionization Boundary
A new listening session is triggered after **30 minutes of playback inactivity**:
$$\Delta t = t_i - t_{i-1} > 30\text{ minutes} \implies \text{New Session}$$
Sessions are classified into a behavioral taxonomy:
- `short_burst`: $\le 2$ tracks or $< 5$ minutes.
- `normal_session`: 3 to 10 tracks.
- `long_session`: $> 10$ tracks and $\ge 30$ minutes.
- `rabbit_hole`: $\ge 4$ unique artists and $\ge 3$ discoveries.
- `album_session`: $\ge 70\%$ of session tracks belonging to the same project ($\ge 3$ tracks).
- `artist_exploration`: $\ge 70\%$ of session tracks belonging to the same artist.

### C. Listening Chronology vs Causality
Listening sequence alone does not prove causality. The engine strictly utilizes non-causal, objective terminology:
- *Discovery pathway*
- *Catalog expansion*
- *Catalyst signal*
- *Re-engagement*
- *Downstream listening*
