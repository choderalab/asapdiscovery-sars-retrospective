# Goals
Assess the effect on protonation state choices on the dockin performance
1. Protein protonation state
2. Ligand protonation state

# Questions
- [ ] How sensitive is the ChemGauss score to differences in ligand protonation states?
- [ ] How sensitive is the ChemGauss score to differences in protein protonation states?
- [ ] How do these differences affect the pose prediction process with POSIT?

# Answers


# Experiments

## 1. Test effect of protonation state of ligand on ChemGauss4 score
`00_testing_ideas/test_chemgauss_score_protonation_states.ipynb`
The protonation state does have an effect but in this example it isn't the one we'd expect.

The protonated His163 should require a deprotonated isoquinoline, but in this case a protonated isoquinoline has a better score (-12) than the deprotonated. This is extra confusing because this means that two positive charges right next to each other aren't being penalized.

