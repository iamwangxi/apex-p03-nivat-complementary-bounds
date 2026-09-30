Complementary complexity bounds for Case B star configurations: convex sections and all quadratic positions

We give complementary bounds for Case B stars in Apex Intelligence's convex Nivat paper (CN, 12 September 2026). The main estimate extends Kari–Szabados (KS) counting to lattice-convex windows in KS's existing configuration class, broader than Case B. The second strengthens CN's quadratic count on arbitrary finite windows. Their maximum weakly dominates Theorem T, strictly on explicit infinite families.

Manuscript v1.1; [repository](https://github.com/iamwangxi/apex-p03-nivat-complementary-bounds), tag `v1.0`. [CN](https://math.apexin.net/papers/convex-nivat.pdf): locally hashed version. KS numbers: *An Algebraic Geometric Approach to Nivat's Conjecture*, [arXiv:1605.05929v1](https://arxiv.org/abs/1605.05929v1).

## 1. A section-count theorem

Use $(T^u c)(z)=c(z+u)$ and $R=\mathbb C[T_1^{\pm1},T_2^{\pm1}]$. Reverse exponents when transferring KS series identities. $P_c(S)$ counts distinct functions $s\mapsto c(u+s)$ over all $u\in\mathbb Z^2$.

Fix a finite-valued integer configuration $c$ with no nonzero period and with $\operatorname{Ann}(c)\ne(0)$. KS Corollary 24 gives
$$
\operatorname{Ann}(c)=\varphi\mathcal H,\qquad
\varphi=\prod_{j=1}^r\varphi_j,\qquad r\ge2,
$$
where the line polynomials have pairwise distinct directions, $\mathcal H$ is an intersection of finitely many maximal ideals (possibly $R$), and $(\varphi)+\mathcal H=R$. Each direction includes its entire grouped line factor. Fix a nonzero $f\in\operatorname{Ann}(c)$ minimal under divisibility: no proper nonunit divisor of $f$ annihilates $c$.

For direction $i$, choose a primitive $v=v_i$ and normalize its grouped factor, up to a Laurent unit, as
$$
\varphi_i=A_i(T^v),\qquad A_i(t)=\sum_{j=0}^{d_i}a_jt^j,
\quad d_i\ge1,\quad a_0a_{d_i}\ne0.
$$
Put $g_i=f/\varphi_i$, $\pi_v(z)=\det(v,z)$, and
$$
w_i=\max_{s\in\operatorname{supp}\varphi}\pi_v(s)
-\min_{s\in\operatorname{supp}\varphi}\pi_v(s)>0.
$$
For every nonempty finite lattice-convex $S=\operatorname{Conv}(S)\cap\mathbb Z^2$, define
$$
E_i=\{z\in\mathbb Z^2:z+\operatorname{supp}g_i\subseteq S\},\qquad
K_i=\#\{t\in\mathbb Z:|E_i\cap\pi_v^{-1}(t)|\ge d_i\},
$$
$$
\ell_i=\max_{a\in\mathbb Z}\min_{a\le t<a+w_i}|S\cap\pi_v^{-1}(t)|,
\qquad \varepsilon_i=\mathbf1[A_i(1)=0].
$$
Empty sections have length zero. Empty erosions, $K_i=0$, $\ell_i=0$, points and segments are allowed. The claim is
$$
\boxed{P_c(S)\ge (K_i+\varepsilon_i)(\ell_i+1).}\tag{SC}
$$
Maximize valid bounds; do not add them.

**Filtered ideal.** Write $f=\varphi h$, $h\in\mathcal H$. If an irreducible factor $p$ of $\varphi$ divided $h$, comaximality would make $p$ invertible modulo $\mathcal H$, hence $h/p\in\mathcal H$. Then $f/p$ would annihilate $c$, contradicting minimality. Thus $\gcd(h,\varphi)=1$. For $c_i=g_i(T)c$, if $qc_i=0$, then $qg_i\in\varphi\mathcal H$ and $\varphi\mid qg_i$. Canceling $\varphi/\varphi_i$ and using coprimality gives $\varphi_i\mid q$. Conversely $\varphi_i c_i=fc=0$, so
$$
\operatorname{Ann}(c_i)=(\varphi_i).
$$
Minimality is essential (KS Lemma 38).

**Disjoint pattern lines.** With $C=\operatorname{Conv}(S)$,
$E_i=(\bigcap_{s\in\operatorname{supp}g_i}(C-s))\cap\mathbb Z^2$ is lattice-convex. Each $v$-section consists of consecutive lattice points. In each of its $K_i$ sections of length at least $d_i$, select $d_i$ consecutive points, obtaining $D_i$ with $|D_i|=d_iK_i$.

No nonzero multiple of $\varphi_i$ can have support in $D_i$: grouping by transverse layer, every nonzero one-variable section of a multiple of $A_i$ has exponent span at least $d_i$, whereas a selected section has span $d_i-1$. Reflections needed in KS's convention preserve this fact. The orthogonality argument of KS Lemma 32 therefore gives full rank $d_iK_i$ for the $D_i$-patterns of $c_i$.

Each pattern line $\{c_i|_{u+kv+D_i}:k\in\mathbb Z\}$ obeys recurrence $A_i$ and spans dimension at most $d_i$. A selected pattern supplies $d_i$ consecutive values per section; nonzero end coefficients determine all previous and next values. Sharing one pattern therefore forces identical pattern lines. Distinct lines are disjoint; full rank requires at least $K_i$.

Because $D_i+\operatorname{supp}g_i\subseteq S$, original patterns determine filtered patterns equivariantly under $v$-translation. Choosing one original line above each disjoint filtered line gives disjoint original lines.

**The conditional extra line.** If $q(T)c_i$ is constant, both $(T^{e_1}-1)q$ and $(T^{e_2}-1)q$ belong to $(\varphi_i)$. The two coordinate binomials are coprime. Comparing irreducible multiplicities gives $\varphi_i\mid q$, so the constant is zero. Thus $c_i$ is normalized. The same orthogonality argument gives rank $d_iK_i+1$ for augmented vectors $(1,c_i|_{u+D_i})$. If $A_i(1)=0$, their constant coordinate satisfies the same recurrence, and a line still spans dimension at most $d_i$. At least $\lceil(d_iK_i+1)/d_i\rceil=K_i+1$ disjoint lines are required. If $A_i(1)\ne0$, retain only $K_i$. For $K_i=0$, one original line exists if $\varepsilon_i=1$; otherwise the bound is zero.

**Patterns per original line.** The primitive $v$ makes $\pi_v$ surjective onto $\mathbb Z$. A stripe consisting of $w_i$ consecutive transverse layers has extreme-layer span $w_i-1$ and cannot contain a translate of $\operatorname{supp}\varphi$; a stripe with one more layer can. It is a maximal-width stripe of KS Lemma 39, so every translate of it is nonperiodic along $v$.

Choose layers attaining $\ell_i$. For every anchor $u$, the translated stripe has a nonperiodic fiber: periodic words on finitely many fibers would have a common period. Its intersection with $u+S$ has at least $\ell_i$ consecutive points. Translation through $kv$ reads all length-$\ell_i$ words; Morse–Hedlund gives $\ell_i+1$ patterns per original line. For $\ell_i=0$, nonemptiness suffices. Multiply by the disjoint-line count to prove (SC).

This modifies KS Lemmas 38 and 40 using Corollary 24 and Lemmas 32 and 39. Actual convex sections replace the rectangular size estimates; their original statements retain their size conditions.

## 2. The Case B interface

A CN star is $\theta=\sum_{i=1}^mF_i:\mathbb Z^2\to\mathbb F_p$, $p$ prime, $m\ge2$, with pairwise nonparallel primitive $v_i$. Each $F_i$ has period $k_iv_i$, $k_i\ge1$, is not doubly periodic, and has possibly unequal doubly periodic tails outside a finite-width strip. Backgrounds can be absorbed into a component. Choose $H_i=\kappa_iv_i$, $\kappa_i\ge1$, preserving its component and all tails (CN Section 0.3); set $D=\prod_i(T^{H_i}-1)$. Case B is $D\mathbf1[\theta=a]=0$ for every color in characteristic zero; only the component sum is mod $p$.

Stars are aperiodic independently of T. The isolating limit along $nH_i$ is $\Xi_i^+=F_i+B_i^+$, with doubly periodic $B_i^+$ and period $H_i$ (CN Section 2.1). A nonzero period $u$ of $\theta$ passes to the limit. Choose $v_i\not\parallel u$: the limit, hence $F_i$, would be doubly periodic, a contradiction.

An integer injection gives $c=w(\theta)$ finite-valued and aperiodic, $Dc=\sum_aw(a)D\mathbf1[\theta=a]=0$, preserving patterns. All Case B stars enter (SC), including unequal tails, higher periods and backgrounds.

To identify KS's $\varphi$ with CN's exceptional-spectrum polynomial, fix instead the *same spectrum-preserving* injection of CN Lemma 2.2, put $\eta=w(\theta)$, and define
$$
A=\prod_i\prod_{\lambda\in\Lambda_i}(T^{v_i}-\lambda),\qquad
Z=\operatorname{Newt}(A)=\sum_i[0,|\Lambda_i|v_i].
$$
We accept CN Lemma 2.4 (every polynomial sending $\eta$ to a constant is divisible by $A$) and Proposition 3.3 ($b_\eta=A\eta$ is doubly periodic) as upstream inputs. Here is the parameter bridge, not a replacement of CN's structure proof. Every annihilator is divisible by $A$. The common polynomial divisor of the KS ideal $\varphi\mathcal H$ is $\varphi$, since a finite-point ideal has no common nonunit polynomial factor; hence $A\mid\varphi$. For two independent periods $u,w$ of $b_\eta$, both $A(T^u-1)$ and $A(T^w-1)$ annihilate $\eta$. Their binomial factors are coprime, so $\varphi\mid A$. Consequently, up to a unit,
$$
\varphi=A,\qquad\operatorname{Ann}(\eta)=A\operatorname{Ann}(b_\eta).
$$
The second identity follows by dividing each annihilator by $A$. When $b_\eta\ne0$, generally $f=A$ is not an annihilator: choose a valid minimal $f=Ah$ and compute $E_i$ from its actual $g_i$. Unit shifts translate erosion. Arbitrary injection alone does not justify $\varphi=A$.

## 3. Fixed convex shapes and strict infinite families

Fix the configuration, minimal filter $f$, and positive-area lattice polygon $P$ before letting $n\to\infty$. Set $S_n=nP\cap\mathbb Z^2$. In a basis $(v,u)$ with $\det(v,u)=1$, define
$$
W_v(P)=\max_P\pi_v-\min_P\pi_v,\qquad
L_v(P)=\max_t\operatorname{length}\{s:sv+tu\in P\}.
$$
Length is measured in $v$-lattice steps. Fixed-filter erosion removes only a bounded-width boundary layer. Except for boundedly many layers at the projection ends, its sections have at least $d_i$ lattice points; hence $K_i(S_n)=nW_v(P)+O(1)$. Polygonal section lengths are piecewise linear. One can select $w_i$ consecutive layers near a longest chord, from the interior even if that chord is on a boundary; their lengths differ from the maximum by $O(1)$. Integer rounding also costs $O(1)$, so $\ell_i(S_n)=nL_v(P)+O(1)$. Therefore
$$
P_c(S_n)\ge n^2\max_i W_{v_i}(P)L_{v_i}(P)-O(n).
$$
The constants depend on the fixed configuration, filter and shape. The area identity in these determinant-one coordinates gives $\operatorname{area}(P)\le W_v(P)L_v(P)$. Equality requires constant section length in the interior: convexity of the left endpoint and concavity of the right endpoint then force both to be affine, giving a parallelogram with sides parallel to $v$.

For any fixed triangle, the section-length graph has integral $WL/2$, including directions parallel to a side. Thus
$$
P_c(nP\cap\mathbb Z^2)\ge2|nP\cap\mathbb Z^2|-O(n).
$$
The error cannot be dropped for finite triangles. Three or more directions guarantee a strict area-coefficient gain for every fixed polygon; with two, only parallelograms along both directions can lack it. This does not imply finite-window equality.

For an explicit fixed configuration, reuse
$$
c(x,y)=\sum_{i=0}^2\mathbf1[y-2ix=i],\qquad v_i=(1,2i).
$$
Intersections have $x=-1/2$, so $c\in\{0,1\}$ encodes its mod-2 Case B star, with zero tails. A finite operator produces finitely many parallel lines per direction; evaluating far from other directions isolates each coefficient. Each component must separately be annihilated, so $\operatorname{Ann}(c)=(A)$, $A=D=\prod_i(T^{v_i}-1)$ and $f=\varphi=A$.

For $S_n=\{(x,y)\in\mathbb Z_{\ge0}^2:x+y\le n\}$, $n=5r\ge20$, use $v_2=(1,4)$. Then $d_2=\varepsilon_2=1$, $w_2=6$, $E_2=S_{n-4}$, and $K_2=|S_{n-4}|-|S_{n-9}|=5n-25$. The section at $y-4x=t$ has length
$$
\max\left(0,\left\lfloor\frac{n-t}{5}\right\rfloor
-\max\left(0,\left\lceil-\frac t4\right\rceil\right)+1\right).
$$
Only $t=0$ can have length $r+1$; layers $0,\ldots,5$ have minimum $r$. Thus $\ell_2=r$ and (SC) gives $n^2+n/5-24$. The all-position bound below is $(n^2+17n-52)/2$, while T gives $(n+1)(n+2)/2+1$. The section bound exceeds both for every $n=5r\ge20$: its difference from the all-position bound is $(n^2-83n/5+4)/2>0$. The configuration and shape do not change with $n$.

## 4. All legal quadratic positions

Fix the Case B star, spectrum-preserving $w$, $\eta,D,A,Z$ above. Accept CN Lemmas 1.1 and 4.2 as supplying a genuine displacement $d$ with
$$
J_d(z)=D_z[\eta(z)\eta(z+d)]\not\equiv0
$$
of finite support. Fix the witness with the same configuration and operators. Convex comparison uses CN Proposition 5.3 and Corollary 6.2: $d=q_1-q_0$, $q_0,q_1\in Z\cap\mathbb Z^2$. Case B implies $J_0=D\eta^2=0$, so $d\ne0$.

For any nonempty finite $S$, with full pattern set $\mathcal L_S$, put
$$
U_S=\operatorname{span}_{\mathbb Q}\{1,\gamma\mapsto w(\gamma(s)):s\in S\},
$$
$$
R_Z(S)=\{r\in\mathbb Z^2:r+Z\subseteq\operatorname{Conv}(S)\},\qquad
T_d(S)=\{s\in S:s+d\in S\}.
$$
Since $0\in Z$, erosion is finite. For any such $S$,
$$
\boxed{P_\theta(S)\ge\dim_{\mathbb Q}U_S+|T_d(S)|
\ge |S|+1-|R_Z(S)|+|T_d(S)|=:B_{\rm quad}(S).}\tag{Q}
$$

**Affine budget.** Relations $\sum_{s\in S}c_s\eta(u+s)=c_0$ for every anchor are the kernel of a finite integer matrix, one row per distinct pattern. Extending scalars from $\mathbb Q$ to $\mathbb C$ preserves its rank. A nonzero relation gives nonzero $F=\sum c_sT^s$ (otherwise also $c_0=0$), and CN Lemma 2.4 gives unique $F=Ag$. Newton additivity yields
$$
Z+\operatorname{Newt}(g)=\operatorname{Newt}(F)\subseteq\operatorname{Conv}(S).
$$
Thus $\operatorname{supp}g\subseteq R_Z(S)$. Mapping a relation to $g$ is injective, since $F$ determines $c_0$. The relation space has dimension at most $|R_Z(S)|$, whence $\dim U_S\ge |S|+1-|R_Z(S)|$. Convexity was unused (CN Lemma 2.5).

**Quadratic independence.** Each $s\in T_d(S)$ defines a legitimate function $\Psi_s(\gamma)=w(\gamma(s))w(\gamma(s+d))$. If a nontrivial rational combination belonged to $U_S$, writing $h(z)=\eta(z)\eta(z+d)$ and evaluating on all anchors would give
$$
\sum_{s\in T_d(S)}a_sh(u+s)=b_0+\sum_{t\in S}b_t\eta(u+t).
$$
Applying $D$ in $u$ annihilates the right side and gives $F(T)J_d=0$ with nonzero $F=\sum a_sT^s$. For $\widehat J_d(X)=\sum_zJ_d(z)X^{-z}$ this becomes $F(X)\widehat J_d(X)=0$, impossible in the Laurent integral domain. Consequently the quadratic functions are independent modulo $U_S$, and their enlarged space has dimension $\dim U_S+|T_d(S)|\le|\mathcal L_S|$. This extends CN Lemma 7.2 from $R_Z(S)+q_0$ to all legal starts; empty $T_d$ is allowed.

For lattice-convex $S$ and the localized witness, $R_Z(S)+q_0\subseteq T_d(S)$, so $B_{\rm quad}\ge|S|+1$, strictly when $|T_d|>|R_Z|$. With $Z$ two-dimensional, points and segments have empty erosion; a singleton gives at least two patterns. For nonconvex $S$, $|T_d(S)|\ge|R_Z(S)|$ is a configuration-dependent sufficient condition for the same bound; its failure is inconclusive.

For rectangles $R_{a,b}=\{0,\ldots,a-1\}\times\{0,\ldots,b-1\}$, write $W,H$ for the coordinate widths of $Z$ and $\alpha=|d_x|,\beta=|d_y|$. Then
$$
|R_Z(R_{a,b})|=(a-W)_+(b-H)_+,\quad
|T_d(R_{a,b})|=(a-\alpha)_+(b-\beta)_+.
$$
Here $x_+=\max(x,0)$. For the fixed three-line example $W=3,H=6,\alpha=\beta=1$, giving $P_c(R_{a,b})\ge ab+5a+2b-16$ for $a\ge4,b\ge7$. Under proportional dilation this improvement is of boundary order.

If $S=S_0\setminus H_0$ has the same convex hull, its erosion is unchanged and precisely the legal edges with at least one endpoint in $H_0$ are lost. At most $2|H_0|$ are lost. Hence $2|H_0|\le |T_d(S_0)|-|R_Z(S_0)|$ suffices for $P_\theta(S)\ge|S|+1$. This hole criterion is conditional, not a general nonconvex Nivat theorem.

## 5. Joint comparison, exact evidence and limitations

For Case B and a convex window, with each term satisfying its own premises,
$$
P_\theta(S)\ge\max\left\{|S|+1,B_{\rm quad}(S),
\max_{i,f}(K_i(S)+\varepsilon_i)(\ell_i(S)+1)\right\}.
$$
The baseline is redundant for a localized witness. Directions, filters, witnesses and methods cannot be summed. Case A retains CN Proposition 1.3's existing $|S|+1$ bound for all nonempty finite windows; Case B arguments do not automatically apply. This Case A result is not new here.

For the same three-line configuration, the portable evidence gives:

| Window | Theorem T | All-position bound | Section bound | Actual patterns |
|---|---:|---:|---:|---:|
| $R_{6,9}$ | 55 | 86 | 60 | 347 |
| $S_{30}$ | 497 | 679 | 882 | 7037 |

On $S_{30}$, $(K_i,w_i,\ell_i)$ are $(23,6,26),(72,4,10),(125,6,6)$, giving 648, 803, 882. Also $|R_Z|=253$, $|T_d|=435$. The reconstructed 12-point witness includes $J_{(1,1)}(-5,-9)=1$. Since $Ac=0$, all affine relations are exactly $Aq$ with support of $q$ in $R_Z$; convexity gives the converse. Hence affine rank is $497-253=244$, and extended rank $244+435=679$ by (Q). This is analytic rank plus geometry, not a 679-order numerical minor; 882 is a theorem bound, not rank or actual complexity.

Global enumeration uses $Q_i=\{y-2ix:(x,y)\in S\}$ and $t_i=i-Y+2iX$. Zero hits give zero. Every single-hit section is realized by moving along $v_i$ while avoiding finitely many forbidden intersections. Multiple hits are exhausted by pairs $t_i\in Q_i,t_j\in Q_j$:
$$
X=\frac{t_j-t_i-(j-i)}{2(j-i)},\qquad Y=i+2iX-t_i.
$$
Retain integer anchors and evaluate all pixels. On $S_{30}$ this gives 6795 distinct multiple-hit anchors and 7062 representatives, deduplicating to 7037 patterns, without finite-box sampling. Their fingerprint is `c68c8a66cce70a8dd0cc9b3b4ed3ceee0ed057cc121c30a01e1c23b13f563646` (lexicographic window order, first point at low bit, sorted integers, 62-byte little-endian blocks).

Reused certificates certify reconstructed matrices by integer minors and rational right kernels. On $R_{6,9}\setminus\{(2,4)\}$ the general bound is **83**, actual affine rank 46 plus 38 quadratic columns gives **84**; T does not apply. Reconstruction/tampering tests cover higher degrees, $\varepsilon=0$, missing layers, periodic background, empty erosion, points and segments. Stress cases test only general SC nonzero-background handling; the Case B parameter bridge is proved above. Tests support implementation, not the general proof.

On this same configuration, KS Lemmas 38 and 40(b), direction $(1,2)$, already give $(3n-12)\lceil(n+1)/2\rceil$ on $R_{n,n}$ for $n\ge12$. At $n=30$: KS 1248, (Q) 1094, (SC) 1296. Existing KS gains are area-order. We claim no comprehensive superiority over previous methods or their optimizations.

Strictness has two obstacles. Fix $k\ge2$: the disjoint supports $L_1=\{(2kt,t)\}$ and $L_2=\{(k+2kt,-t)\}$ give a fixed mod-2 Case B star. Nonzero columns have spacing $k$ and one point each. Every $R_{k,N}$ contains at most one point; every singleton and zero pattern occurs. Hence $P(R_{k,N})=kN+1$ for all $N\ge1$, infinitely many two-dimensional windows. Changing $k$ to produce large square equalities changes the configuration.

Separately fix $c(x,y)=\mathbf1[y=0,x\equiv0\pmod2]+\mathbf1[x=1,y\equiv0\pmod2]$, a Case B star with disjoint supports and tangential periods 2. For $M,N\ge5$, both supports are identifiable: both visible give $MN$ patterns, only horizontal $2N$, only vertical $2M$, and neither one. Thus $P_c(R_{M,N})=MN+2M+2N+1$, with square area coefficient 1. This prevents a universal proportional improvement for fixed Case B stars, consistent with the two-direction parallelogram exception.

## 6. Attribution, scope and AI assistance

(SC) extends KS counting to convex shapes; (Q) strengthens CN Lemmas 2.5 and 7.2. Configuration and prior certificates are reused. The two estimates serve one complexity improvement; no organizer approval or prize eligibility is asserted.

Search records (30 September 2026) found no exact-form antecedent in checked queries/passages. No new search was done here. Priority is unverified; equivalent optimized estimates may exist. Rank/stripe methods and rectangular area-order gains are established.

No optimality, general nonconvex Nivat result or higher periodicity threshold is claimed. A single-point defect already has $P(S)=|S|+1$ without periodicity. CN's structure proof is not replaced, nor its Section 8 reduction revalidated or extended. Its divisibility and witness localization are explicit inputs.

Codex/GPT assisted derivations, searches, certificates, this proof and its evidence/checker. Claude coordinated scope, without independently rederiving the mathematics. A fresh gpt-6.1-sol context completed adversarial review with no mathematical blockers: `对抗复核-v1.0.md`, bound to v1.0 SHA-256 `3bd81a166c53f8a073ad893eeaef24fe05b83468023151b3b550db385d9fd52c`. v1.1 changes wording only; formulas and proof sections 1–4 are unchanged.
