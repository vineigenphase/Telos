-- 047_mock_a_free.sql
-- Mock A becomes free to signed-in users.
--
-- This overrides the settled "£1 per paper" decision for Mock A ONLY. The
-- reasoning, from the owner on 29 September 2026: Telos has about a hundred
-- users and no paying customers, and advertising is the bottleneck rather than
-- the product. A free full mock is the lead magnet for the National Mock on
-- 4 October; what people pay for afterwards is Pro, and later mocks.
--
-- Mock B and anything after it stay at £1 each, or included with Pro. Pro still
-- includes every paper, because a plan change must never take something away
-- from a subscriber.
--
-- Matched on paper_code, naming exactly the five Mock A papers, rather than on
-- `series`. A series match would be shorter and would silently free any future
-- paper that someone labelled "Telos Mock A" — and this migration changes what
-- the app charges, so it says precisely which five papers it means.
--
-- Free does not mean public: every Exam Mode route is @login_required, so a
-- free paper still needs an account. That is the whole point of the lead
-- magnet.
--
-- Idempotent: setting a price to the value it already holds changes nothing.

UPDATE exam_papers
   SET price_pence = 0
 WHERE paper_code IN ('TMUA-P1-A', 'TMUA-P2-A',
                      'ESAT-M1-A', 'ESAT-M2-A', 'ESAT-PHY-A');

-- A loud failure beats a quiet one: if a paper_code is ever renamed, this
-- migration would silently free nothing, and the launch would go out charging
-- for the lead magnet.
DO $$
DECLARE
    freed INT;
BEGIN
    SELECT COUNT(*) INTO freed
      FROM exam_papers
     WHERE price_pence = 0
       AND paper_code IN ('TMUA-P1-A', 'TMUA-P2-A',
                          'ESAT-M1-A', 'ESAT-M2-A', 'ESAT-PHY-A');
    IF freed <> 5 THEN
        RAISE EXCEPTION
            'expected 5 free Mock A papers, found %. Check paper_code values.',
            freed;
    END IF;
END $$;
