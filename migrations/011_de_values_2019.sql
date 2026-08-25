-- 011_de_values_2019.sql
-- Official D and E for the June 2019 Edexcel rows.
--
-- Split from 010 because 2019's table is laid out differently: the header is
-- "Max Mark A B C D E U" with no A* column at component level, and the paper
-- labels are zero-padded. The A* figures already stored for 2019 did not come
-- from this document — Pearson does not publish one at component level for that
-- series — and are left untouched.
--
-- Every value here was checked by re-reading the official A, B and C for the
-- same row and requiring them to equal what is already stored, so a column
-- shift in the parsing would have written nothing at all.
--
-- 7 rows. Idempotent.

UPDATE grade_boundaries SET d_boundary = 23, e_boundary = 15
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'CP1' AND year = '2019';
UPDATE grade_boundaries SET d_boundary = 21, e_boundary = 14
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'CP2' AND year = '2019';
UPDATE grade_boundaries SET d_boundary = 28, e_boundary = 20
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FM1' AND year = '2019';
UPDATE grade_boundaries SET d_boundary = 25, e_boundary = 17
 WHERE subject = 'Further Maths' AND board = 'Edexcel' AND paper_code = 'FS1' AND year = '2019';
UPDATE grade_boundaries SET d_boundary = 25, e_boundary = 15
 WHERE subject = 'Maths' AND board = 'Edexcel' AND paper_code = 'Pure 1' AND year = '2019';
UPDATE grade_boundaries SET d_boundary = 22, e_boundary = 13
 WHERE subject = 'Maths' AND board = 'Edexcel' AND paper_code = 'Pure 2' AND year = '2019';
UPDATE grade_boundaries SET d_boundary = 25, e_boundary = 15
 WHERE subject = 'Maths' AND board = 'Edexcel' AND paper_code = 'Stats&Mech' AND year = '2019';
