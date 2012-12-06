import difflib
import re
import textwrap

def raw_contents():
    with open("pubs.txt") as f:
        return f.read()

sameyear = lambda p, q: p["year"] == q["year"]
dist = lambda p, q: difflib.SequenceMatcher(None, p["title"], q["title"]).ratio()


def display_close_matches(pubs, skip_first):
    studied = []
    found = 0
    for p in pubs:
        for q in [q for q in pubs
                  if p != q and sameyear(p, q) and dist(p, q) > 0.9 and q not in studied]:
            if found >= skip_first:
                print
                print p
                print q
            found += 1
        studied.append(p)
    print "Found %d duplicates, skipped the first %d." % (found, skip_first)


def main():
    raw = raw_contents()
    pubs = re.split('\n\s*(\n+)\s*', raw)
    
    n = 0
    tw = textwrap.TextWrapper(60,
                              subsequent_indent=' ' * 8,
                              break_long_words=False,
                              break_on_hyphens=False)

    formatted = []
    for p in pubs: # [700:]:
        p = p.strip()
        if not p:
            continue

        # Get rid of inspire URL
        p = re.sub(r'%\\href{.+?}{.+?}', '', p, re.M|re.S)
        # Get rid of double dates
        p = re.sub(r'\((\d{4})\)\.\s*%\(.+?\)', r'(\1).', p, re.M|re.S)
        # Find all dates:
        numbers = re.findall(r'[^\d](\d{4})[^\d]', p, re.M|re.S)
        numbers = map(int, numbers)
        numbers = filter(lambda x: 1988 < x < 2019, numbers)
        # Make sure latest date appears at end if no other date is shown there:
        latest = sorted(numbers)[-1]
        if not re.search(r'\d{4}\).$', p):
            p = p + " (%s)." % latest
            n += 1
        out = tw.fill(p)
        assert re.search('\d{4}\)\.$', out)
        def no_double_space(x):
            return re.sub(r'\s\s+', ' ', x, re.M|re.S)
        
        def title(x):
            return no_double_space(re.search(r"``(.+?)''", x, re.M|re.S).group(1))

        def cleanrev(s):
            s = s.replace("\\", '')
            s = s.replace("~", " ")
            return s
        
        def isref(body):
            for t in ["Nature", "Science", "Phys. Rev.", "Z. Phys", "Phys. Lett.",
                      "Nucl. Instrum. Meth"]:
                if t in cleanrev(body):
                    return True
        #print out
        #print
        formatted.append({"txt": out,
                          "year": int(latest),
                          "title": title(out),
                          "isref": isref(out)})

    formatted = sorted(formatted, key=lambda t: -t["year"])
    # print len(formatted), "pubs", [p["year"] for p in formatted]
    # for p in formatted:
    #     print "*" if p["isref"] else " ", p["year"], p["title"]
    # print; print
    display_close_matches(formatted, 4)

    refereed = filter(lambda x: x["isref"], formatted)
    conferns = filter(lambda x: not x["isref"], formatted)

    print "REFEREED"
    for p in refereed:
        print p["txt"] + "\n"

    print "OTHERS"
    for p in conferns:
        print p["txt"] + "\n"
    
        

if __name__ == "__main__":
    main()
