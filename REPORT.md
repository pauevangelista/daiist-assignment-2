# Assignment 2 Report

- **Name**: Paula Evangelista
- **Student ID**: 20150
- **Email**: pevangelista.ieu2022@student.ie.edu
- **Group**: [BBADBA 5A]

## Business problem, and the cost of being wrong

I picked a hygiene gate at the entrance of the filling hall in a luxury cosmetics
plant. A camera takes one photo of each operator before they go in, and the model
decides one of three things: **pass** (mask on, the door opens), **fail** (no mask,
the door stays shut until they put one on) or **review** (the model is not sure, so
a supervisor looks at the photo). The model only checks the mask. It does not
identify anyone.

The class I care about is **NO-Mask**, because that is the one I must not miss.

The two mistakes do not cost the same:

- **Missing a no-mask (false negative): about €300.** If an unmasked person gets
  in, there is a small chance the product gets contaminated and a batch is put on
  hold. I assumed a 2% chance of that and a €15,000 cost per hold, so the expected
  cost is 0.02 × 15,000 = €300.
- **False alarm (false positive): about €1.** A masked person is stopped by
  mistake and a supervisor needs around 30 seconds to check, at roughly €25 an
  hour, plus a little waiting time for the operator.

So a miss is about 300 times worse than a false alarm. That is why I will set the
threshold low: I would rather stop a few people by mistake than let one through.
It is also why I use a review band. If I only used a low threshold, I would stop
too many masked people, so the uncertain cases go to a person instead.

I assume 2% of entries are without a mask. This is an assumption, not data. Most
people comply, but a few are rushed or have just taken it off. My headline metric
is recall on NO-Mask, together with the share of cases sent to review. I do not
use overall mAP as the main number because it treats both classes the same and
hides this asymmetry.

The assumption that would change my answer the most is the cost of a miss. If a
miss cost much less (for example, a 0.2% chance of a hold), the best threshold
would be higher and fewer cases would need review.

## Dataset

- **Workspace / project / version:** `roboflow-universe-projects` /
  `mask-wearing-iskms` / **version 6** ("roboflow train v3")
- **Link:** https://universe.roboflow.com/roboflow-universe-projects/mask-wearing-iskms/dataset/6
- **Task:** object detection with 2 classes, `Mask` and `NO-Mask`. Each box is
  drawn around a face.
- **What one image represents:** one photo of one or more people, taken at
  close range, with a box around each face and a label saying whether that
  face has a mask on. Many of the images look like indoor webcam-style photos.

**Why it serves my problem and does not just resemble it.** At the gate, the
decision is whether a face has a mask on or not, and this dataset is labelled
for exactly that, with the two classes I need. The boxes also let me turn the
model output into a per-image decision: an image fails if it contains a
NO-Mask detection above the threshold, and passes if it has a Mask detection
and no NO-Mask. The photos are close and mostly frontal, which is close to what
a gate camera would see.

**Where it only partly fits.** I am being honest about three gaps:
- The masks are everyday masks. A cleanroom would also need hairnets, hoods
  and goggles, which this dataset does not cover, so I only claim to check
  the mask.
- The lighting and backgrounds are not those of a plant.
- Some images contain several people, while the gate would only see one.

I chose version 6 because it's valid and test splits are original images, and
only the training split is augmented. That means the test results are not
inflated by copies of training images.

## What the dataset's composition implies

| Split | Images | Mask instances | NO-Mask instances |
|---|---|---|---|
| Train | 7,413 | 5,932 | 4,693 |
| Valid | 706 | 554 | 505 |
| Test | 353 | 329 | 218 |

**Object size.** I measured this on the test split (547 boxes). The median face
box is about 12% of the image width and 19.5% of the image height, which is
about 2% of the image area, or roughly 77 x 125 pixels after the 640x640 resize.
58% of the boxes cover less than 5% of the image area. So the faces are small,
and I expect this to hurt recall, especially on NO-Mask, because a small face
with a hidden or blurry mouth area is the hardest case to judge and it is also
the mistake that costs me the most.

**What the numbers tell me.**
- **The training counts are inflated.** Train is augmented three times, so the
  7,413 images are about 2,470 real ones. Valid and test are original images,
  so the test results are not inflated by copies.
- **Both classes have enough data to train on.** Neither is close to 100
  instances, which is where I would stop trusting a number.
- **NO-Mask is the thin class in test, with 218 instances.** Its recall can
  move by a few points just from which images ended up in the split. For a
  recall near 90%, the 95% interval is about plus or minus 4 points
  (1.96 x sqrt(0.9 x 0.1 / 218)). So I will not treat small differences
  between models, or small changes in the threshold, as real.

**Does the test split look like what I would really see?** No, in two ways.
- **Class mix.** About 40% of test instances are NO-Mask (218 of 547), but at my
  gate I assume only 2% of entries are without a mask. Test precision would
  therefore be far too optimistic, because in real life almost every alarm would
  be a masked person. Before I put any euro value on the confusion matrix, I
  reweight it to the 2% base rate.
- **Face size.** Many faces here are small (median about 2% of the image area),
  so the photos are often wider scenes than what a gate camera would capture. A
  gate camera at close range gives larger faces, so on this point the test is
  probably harder than my real use case. This is the one place where my results
  are likely conservative, not optimistic.

**What I can't conclude from my results.**
- I can't say how many false alarms the gate would really produce. I can only
  estimate it after reweighting to the assumed 2% base rate.
- I can't say it works under plant lighting or with cleanroom clothing
  (hairnets, hoods, goggles), because the dataset has neither.
- I can't rule out that the same person appears in both train and test. I saw
  the same person several times in the preview images, so if this happens, the
  test score is a bit optimistic.
- I can't conclude small differences in NO-Mask recall, because of
  the 218 test instances.

## Finetuning and baselines

*Which model and task (detection or classification) and why. A results table on
the same test split: your finetuned model, the pretrained COCO model zero-shot,
and a trivial baseline. What changed, and whether the gap is as large as you
expected.*

## Per-class evaluation and failure modes

*Per-class AP50, or per-class precision/recall and the confusion matrix.
Which class carries the headline number, which one is dragging, and what the
model actually confuses with what. Show where it breaks, not just that it
works.*

## Cost matrix and operating point

*Your euro cost for each kind of error and where each figure came from. The
base rate you assumed. The cost-against-threshold sweep, and the operating
point you chose. State the assumption that would most change your answer if it
were wrong.*

## What a person still has to check

*Your two thresholds, and what share of cases they send to a person. How many
that is per day, how long one takes to check, and how many people that needs.
Is that realistic? Then your design priced against the three alternatives:
doing nothing, having a person check everything, and letting the model decide
on its own.*

## Limitations & next steps

*Real limitations you found, and concretely how you'd address each one with
more time or data. Not generic hedging.*

## Generative AI use disclosure

*Per the syllabus AI Policy: what you used and how, or "no AI content used."*
