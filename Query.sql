
/* suspect */
select distinct newad.CWID, newad.First, newad.Middle, newad.Last  from  newad_1108 newad
join campus cp
    on newad.First = cp.First
    and newad.Last = cp.Last
    and not (cp.Middle != newad.Middle and cp.Middle != '' and newad.Middle != '')
where cp.CWID != newad.CWID;

/* continuing */
select distinct newad.CWID, newad.First, newad.Middle, newad.Last
from newad_1108 newad
join campus cp
    on newad.CWID = cp.CWID
;

/* brand new */
select distinct raw.CWID, raw.First, raw.Middle, raw.Last
from raw_newad_1108 raw
where raw.CWID not in
  (
  /* suspect */
    select distinct newad.CWID
    from newad_1108 newad
    join campus cp
        on newad.First = cp.First
        and newad.Last = cp.Last
        and not (cp.Middle != newad.Middle and cp.Middle != '' and newad.Middle != '')
    where cp.CWID != newad.CWID

  union

  /* continuing */
    select distinct newad.CWID
    from newad_1108 newad
    join campus cp
        on newad.CWID = cp.CWID

  )
