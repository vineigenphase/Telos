-- 046_mock_a_topic_groups.sql
-- Group the Mock A questions into topics a student can act on.
--
-- Every question carried a topic of its own, so the results screen's "By
-- topic" section was twenty rows of 1/1 — exactly the information already in
-- the question list below it, arranged differently and useful to nobody. Six
-- to eight groups per paper make it a reading: "trigonometry 1/3" tells a
-- candidate what to revise tonight in a way that "cosine rule & the ambiguous
-- case 0/1" never did.
--
-- The groups are built from the labels that were already there rather than
-- invented, and each original label is kept in the paper's JSON under `detail`
-- so nothing is lost from the source of truth.
--
-- Updated in place, matched on (paper_code, n), rather than reloading the
-- papers through the admin screen. That is not a preference. loader.upsert()
-- deletes a paper's questions and reinserts them, and
-- exam_responses.question_id REFERENCES exam_questions(id) ON DELETE CASCADE —
-- so a reload would take every answer of every attempt already sat with it,
-- silently, and the attempt would still be there showing a score it could no
-- longer justify.
--
-- Idempotent: setting a topic to the value it already holds changes nothing.

UPDATE exam_questions SET topic = 'Indices, logarithms & exponentials' WHERE n = 1 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Indices, logarithms & exponentials' WHERE n = 11 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Algebra & equations' WHERE n = 2 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Algebra & equations' WHERE n = 3 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Algebra & equations' WHERE n = 4 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Algebra & equations' WHERE n = 20 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Sequences & series' WHERE n = 5 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Sequences & series' WHERE n = 6 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Coordinate geometry & circles' WHERE n = 7 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Coordinate geometry & circles' WHERE n = 15 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Coordinate geometry & circles' WHERE n = 18 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Trigonometry' WHERE n = 8 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Trigonometry' WHERE n = 9 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Trigonometry' WHERE n = 10 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Calculus' WHERE n = 12 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Calculus' WHERE n = 13 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Calculus' WHERE n = 14 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Graphs & transformations' WHERE n = 16 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Graphs & transformations' WHERE n = 17 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Probability' WHERE n = 19 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P1-A');
UPDATE exam_questions SET topic = 'Logic & conditionals' WHERE n = 1 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Logic & conditionals' WHERE n = 3 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Logic & conditionals' WHERE n = 8 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Logic & conditionals' WHERE n = 11 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Logic & conditionals' WHERE n = 18 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Logic & conditionals' WHERE n = 20 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Quantifiers & negation' WHERE n = 2 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Quantifiers & negation' WHERE n = 6 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Quantifiers & negation' WHERE n = 10 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Flawed proofs & common errors' WHERE n = 4 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Flawed proofs & common errors' WHERE n = 9 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Flawed proofs & common errors' WHERE n = 13 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Flawed proofs & common errors' WHERE n = 19 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Counterexamples & conjecture' WHERE n = 5 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Counterexamples & conjecture' WHERE n = 12 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Number & divisibility' WHERE n = 7 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Number & divisibility' WHERE n = 15 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Algebraic & graphical reasoning' WHERE n = 14 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Algebraic & graphical reasoning' WHERE n = 16 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Algebraic & graphical reasoning' WHERE n = 17 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'TMUA-P2-A');
UPDATE exam_questions SET topic = 'Number' WHERE n = 2 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Number' WHERE n = 3 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Number' WHERE n = 4 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Number' WHERE n = 5 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Number' WHERE n = 27 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Ratio, proportion & percentages' WHERE n = 6 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Ratio, proportion & percentages' WHERE n = 7 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Ratio, proportion & percentages' WHERE n = 8 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Algebra & sequences' WHERE n = 9 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Algebra & sequences' WHERE n = 10 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Algebra & sequences' WHERE n = 11 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Algebra & sequences' WHERE n = 12 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Algebra & sequences' WHERE n = 13 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Coordinate geometry & vectors' WHERE n = 14 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Coordinate geometry & vectors' WHERE n = 15 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Coordinate geometry & vectors' WHERE n = 22 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Geometry, angles & trigonometry' WHERE n = 16 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Geometry, angles & trigonometry' WHERE n = 17 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Geometry, angles & trigonometry' WHERE n = 20 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Mensuration & 3D' WHERE n = 1 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Mensuration & 3D' WHERE n = 18 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Mensuration & 3D' WHERE n = 19 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Mensuration & 3D' WHERE n = 21 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Statistics & probability' WHERE n = 23 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Statistics & probability' WHERE n = 24 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Statistics & probability' WHERE n = 25 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Statistics & probability' WHERE n = 26 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M1-A');
UPDATE exam_questions SET topic = 'Surds, indices, logarithms & exponentials' WHERE n = 1 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Surds, indices, logarithms & exponentials' WHERE n = 2 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Surds, indices, logarithms & exponentials' WHERE n = 18 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Surds, indices, logarithms & exponentials' WHERE n = 19 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Surds, indices, logarithms & exponentials' WHERE n = 20 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Algebra & polynomials' WHERE n = 3 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Algebra & polynomials' WHERE n = 4 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Algebra & polynomials' WHERE n = 5 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Algebra & polynomials' WHERE n = 6 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Sequences & series' WHERE n = 7 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Sequences & series' WHERE n = 8 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Sequences & series' WHERE n = 9 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Sequences & series' WHERE n = 10 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Coordinate geometry & circles' WHERE n = 11 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Coordinate geometry & circles' WHERE n = 12 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Coordinate geometry & circles' WHERE n = 13 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Trigonometry' WHERE n = 14 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Trigonometry' WHERE n = 15 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Trigonometry' WHERE n = 16 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Trigonometry' WHERE n = 17 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Differentiation' WHERE n = 21 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Differentiation' WHERE n = 22 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Differentiation' WHERE n = 23 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Differentiation' WHERE n = 27 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Integration' WHERE n = 24 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Integration' WHERE n = 25 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Integration' WHERE n = 26 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-M2-A');
UPDATE exam_questions SET topic = 'Electricity & circuits' WHERE n = 1 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Electricity & circuits' WHERE n = 2 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Electricity & circuits' WHERE n = 3 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Electricity & circuits' WHERE n = 4 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Electricity & circuits' WHERE n = 5 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Magnetism & induction' WHERE n = 6 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Magnetism & induction' WHERE n = 7 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Magnetism & induction' WHERE n = 8 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Magnetism & induction' WHERE n = 9 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Motion, forces & momentum' WHERE n = 10 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Motion, forces & momentum' WHERE n = 11 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Motion, forces & momentum' WHERE n = 12 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Motion, forces & momentum' WHERE n = 13 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Motion, forces & momentum' WHERE n = 14 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Motion, forces & momentum' WHERE n = 18 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Energy, work & power' WHERE n = 15 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Energy, work & power' WHERE n = 16 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Energy, work & power' WHERE n = 17 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Thermal physics' WHERE n = 19 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Thermal physics' WHERE n = 20 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Matter & pressure' WHERE n = 21 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Matter & pressure' WHERE n = 22 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Matter & pressure' WHERE n = 23 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Waves' WHERE n = 24 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Waves' WHERE n = 25 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Radioactivity' WHERE n = 26 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
UPDATE exam_questions SET topic = 'Radioactivity' WHERE n = 27 AND paper_id = (SELECT id FROM exam_papers WHERE paper_code = 'ESAT-PHY-A');
