#set page(
  paper: "us-letter",
  margin: (top: 0.36in, bottom: 0.36in, left: 0.46in, right: 0.46in),
)
#set text(
  font: ("Segoe UI", "Arial"),
  size: 8.15pt,
  fill: rgb("#1a1a1a"),
)
#set par(
  justify: true,
  leading: 0.39em,
)

#let pc-green = rgb("#1e6b3a")
#let pc-dark = rgb("#1b2420")
#let pc-gold = rgb("#d9532f")
#let pc-light = rgb("#f4f8f5")
#let pc-border = rgb("#c5d6cb")

// ==================== PAGE 1: AGREEMENT ====================

#grid(
  columns: (1.0in, 1fr),
  column-gutter: 12pt,
  align: (left + horizon, left + horizon),
  image("images/logo.png", width: 0.95in),
  [
    #text(size: 14.5pt, weight: "bold", fill: pc-dark)[POCKET CASH CARDS — CONSIGNMENT & BAILEE AGREEMENT] \
    #v(2pt)
    #text(size: 9.2pt, weight: "semibold", fill: pc-green)[Carter, Bryan, Marshall & Grayson Counties • Local In-Person Meet-Up • getpocketcash.com] \
    #v(2pt)
    #text(size: 8pt, fill: rgb("#555555"))[Zion Hard-Case Transport • Locked Fire-Rated Safe Custody • 60,000-Slot eBay Store • Custom 1080p Video Included]
  ]
)

#v(3pt)
#line(length: 100%, stroke: 1.5pt + pc-green)
#v(3pt)

// Quick Rate Summary Bar
#block(
  width: 100%,
  fill: pc-light,
  stroke: 0.8pt + pc-border,
  radius: 4pt,
  inset: (x: 8pt, y: 4.5pt),
)[
  #grid(
    columns: (1fr, 1.15fr, 1fr, 1fr),
    column-gutter: 6pt,
    align: center + horizon,
    [
      #text(size: 7.3pt, weight: "bold", fill: pc-green)[UPFRONT LISTING FEE] \
      #text(size: 9.2pt, weight: "bold")[\$5.00 / Card] \
      #text(size: 6.8pt)[Paid at intake (Non-refundable)]
    ],
    [
      #text(size: 7.3pt, weight: "bold", fill: pc-green)[7-DAY AUCTION TIERS] \
      #text(size: 9.2pt, weight: "bold")[15% (\$500+) / 25% Std] \
      #text(size: 6.8pt)[Keep 85% (\$500+) or 75% • 1 Free Relist]
    ],
    [
      #text(size: 7.3pt, weight: "bold", fill: pc-green)[BUY-IT-NOW (OPTIONAL)] \
      #text(size: 9.2pt, weight: "bold")[35% of Net Proceeds] \
      #text(size: 6.8pt)[\$75+ Min • Keep 65% • 90-Day Safe]
    ],
    [
      #text(size: 7.3pt, weight: "bold", fill: pc-green)[ZELLE PAYOUT OPTIONS] \
      #text(size: 9.2pt, weight: "bold")[Monthly (\$0 Fee)] \
      #text(size: 6.8pt)[Or Fast Payout (5% / \$5 min)]
    ],
  )
]

#v(4pt)

#let clause(num, title, body) = [
  #block(spacing: 3.4pt, breakable: false)[
    #text(weight: "bold", fill: pc-dark)[#num. #title.] #body
  ]
]

#clause("1", "LISTING FEE & SCOPE")[
  Consignor delivers the trading cards listed on Schedule A to Pocket Cash Cards ("Pocket Cash") at an agreed local meet-up to sell on eBay as Consignor's agent and bailee for mutual benefit. Consignor pays a non-refundable *\$5.00 per card Listing Fee* at intake (Cash or Zelle), which is earned upon logging and not credited against commission. The fee covers intake, front/back imaging, custom listing video, safe custody, and either: (a) one 7-day eBay auction plus one (1) free 7-day relist if unsold, or (b) one 30-day Buy-It-Now listing. Pocket Cash may decline any card or price unlikely to clear fees and expenses.
]

#clause("2", "PRICING, STARTING BIDS & RELISTS")[
  Consignor sets the Starting Bid (*\$15.00 minimum*; no hidden eBay reserves) or Buy-It-Now price (*\$75.00 minimum*) for each card on Schedule A. If a 7-day auction receives no bids, Consignor receives one (1) free 7-day relist (and may lower the Starting Bid). After the included listing(s), Consignor may either arrange return of an unsold card at no charge or prepay *\$3.00 per card* for each additional 7-day auction or 30-day Buy-It-Now cycle (maximum 4 total cycles per card). Cards cannot be withdrawn while a listing is live.
]

#clause("3", "NON-PAYING BUYER PROTECTION")[
  If a winning bidder fails to pay and eBay cancels the order for non-payment, that cycle does not count as an unsold listing and does not consume Consignor's free relist or trigger the \$3.00 relist fee. Pocket Cash will relist the card at no charge (or send a Second Chance Offer at or above Consignor's Starting Bid).
]

#clause("4", "NET PROCEEDS & TIERED COMMISSION")[
  *"Net Proceeds"* equals the Item Sale Price plus Buyer-Paid Shipping, *MINUS*: (a) actual eBay Final Value Fees and order fees shown on the eBay order record, (b) the actual cost of the shipping, insurance, and signature label, and (c) a flat *\$1.50 per sold card Packaging & Materials fee* retained by Pocket Cash (covering penny sleeve, rigid holder, mailer, and label). Sales tax collected by eBay is excluded. Pocket Cash retains *15% of Net Proceeds* on High-End Graded Slab Auctions selling for *\$500.00+* (*Consignor keeps 85%*), *25% of Net Proceeds* on Standard Auctions selling for *\$15.00–\$499.99* (*Consignor keeps 75%*), and *35% of Net Proceeds* on Buy-It-Now sales (*Consignor keeps 65%*; minimum \$5.00 commission per sold card, capped at Net Proceeds; if Net Proceeds are zero or negative, payout is \$0 and Consignor owes no deficit).
]

#clause("5", "MONTHLY STANDARD PAYOUT ($0 FEE)")[
  Standard Payout Day is the *first Friday of each month* (or next business day if a bank holiday) via *Zelle only* to Consignor's verified phone or email below (no cash or store credit). Payout Day pays every sale whose hold window cleared in the prior calendar month. A sale's hold window clears when eBay funds have settled in Pocket Cash's bank account AND tracking shows Delivered for *14 days* (or *30 days* for cards sold at \$250.00 or more) with no open return, claim, or payment dispute.
]

#clause("6", "OPTIONAL FAST PAYOUT (UPON VERIFIED DELIVERY — FEE APPLIES)")[
  For sales with a Consignor Payout of *\$250.00 or less* (or higher only if Consignor has other unsold cards in custody whose aggregate Custody Cap value equals or exceeds the advance; max \$500.00 in unsettled Fast Payouts per 30 days), Consignor may opt in to receive early Zelle payout once tracking shows *Delivered*, 3 days have passed with no open claim, and eBay has released the funds. *Fast Payout Fee: 5% of the Consignor Payout (\$5.00 minimum)*, deducted directly from the payout and non-refundable.
]

#clause("7", "RETURNS, CLAIMS & CLAWBACK OFFSET")[
  If a buyer return, eBay claim, or payment dispute reverses a sale after Zelle payout, Consignor agrees to repay that payout within 7 days of notice. Until repaid, Pocket Cash may deduct any amount owed from current or future payouts and hold the returned card and Consignor's other cards in custody; if unpaid after 30 days, Pocket Cash may auction held cards starting at \$0.99 and retain what is owed. Return postage is deducted from Consignor unless caused by a Pocket Cash listing or packing error.
]

#clause("8", "OUTBOUND SHIPPING LOSS OR DAMAGE (CARRIER TRANSIT)")[
  Pocket Cash ships every sold card tracked in a penny sleeve, rigid holder, and padded mailer or box via USPS Ground Advantage or Priority Mail (which includes up to \$100.00 carrier insurance). For any card selling over *\$100.00*, Pocket Cash purchases carrier or third-party insurance covering the sale price, deducted as a shipping expense under Section 4. Safe custody ends at the carrier's acceptance scan. If the carrier loses or damages a card in transit and the buyer is refunded, the sale is canceled and Pocket Cash files the insurance claim within 30 days. *Pocket Cash's liability to Consignor for transit loss or damage is strictly limited to the insurance proceeds actually received from the carrier*, which are treated as the sale price and paid out under Sections 4–5. Pocket Cash owes \$0 out of its own funds while a claim is pending or if a claim is denied or paid short, unless Pocket Cash failed to pack, track, or insure the card as required herein.
]

#clause("9", "SAFE CUSTODY & LIABILITY CAP (CARD LADDER / $200.00 MAXIMUM — NO DECLARED VALUE)")[
  Cards are transported in a protective hard case and stored in Pocket Cash's locked, fire-rated safe. While in Pocket Cash's custody, maximum liability for physical loss, theft, or damage is strictly limited to the *LOWEST* of the following (determined by Pocket Cash as of the date of loss; *no consignor-declared value is used*): *(a)* the *Card Ladder* value for the exact logged slab company and grade, or, if ungraded, the Card Ladder Raw/Near-Mint value *ONLY* when logged as "Raw NM" on Schedule A (ungraded cards are never valued at graded prices); *(b)* if logged as "Raw LP-or-Worse" or not indexed on Card Ladder, the verifiable 30-to-90-day average of eBay sold comps (last 5 sales) for that card in its logged condition (or Consignor's Schedule A Starting Bid/BIN price if lower); or *(c)* *\$200.00 per card* (subject to a *\$1,000.00 aggregate cap per Consignor*). Consignor acknowledges that any card worth over \$200.00 is still capped at \$200.00 in custody unless Consignor carries separate personal insurance. *Consignor Initials on \$200.00/Card Custody Cap: \_\_\_\_\_\_\_\_\_*
]

#clause("10", "TITLE WARRANTY, NO SHILL BIDDING, 90-DAY UNCLAIMED RULE & LAW")[
  Consignor warrants full ownership and authenticity of each card and agrees that neither Consignor nor anyone acting for Consignor will bid on Consignor's listings (violation forfeits all fees and terminates this agreement). Unsold BIN cards left past 90 days incur a *\$2.00/card/month* storage fee. Any card not reclaimed within 14 days of a return notice or left past 90 days with unpaid fees may, after 14 days' text/email notice, be liquidated in a 7-day auction starting at \$0.99 and paid out under Sections 4–5. Governed by Oklahoma law; exclusive venue in Bryan County, Oklahoma.
]

#v(3pt)
#block(
  width: 100%,
  stroke: 1pt + pc-dark,
  radius: 4pt,
  inset: 6.5pt,
  fill: rgb("#fafafa"),
)[
  #text(size: 8.3pt, weight: "bold", fill: pc-dark)[PAYOUT & INTAKE VERIFICATION (Must Match Consignor's Government Photo ID)] \
  #v(3pt)
  #text(size: 8.3pt)[
    *Payout Election:* #h(8pt) ☐ *Standard Monthly Zelle (\$0 Fee — 1st Friday)* #h(14pt) ☐ *Fast Payout on Eligible Sales (5% Fee, \$5.00 Min)*
  ] \
  #v(4pt)
  #grid(
    columns: (1.1fr, 1.1fr, 0.8fr),
    column-gutter: 10pt,
    row-gutter: 6.5pt,
    [*Consignor Name:* \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_],
    [*Zelle Phone / Email:* \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_],
    [*Phone:* \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_],
    [*Gov Photo ID Checked:* ☐ Yes #h(6pt) *W-9:* ☐ Yes ☐ N/A],
    [*Cards Logged (Sched. A):* \_\_\_\_ × \$5 = *\$*\_\_\_\_\_\_\_],
    [*Intake Paid:* ☐ Cash #h(4pt) ☐ Zelle],
    [*Consignor Signature:* \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_],
    [*Pocket Cash (David Lane):* \_\_\_\_\_\_\_\_\_\_\_\_\_\_],
    [*Date:* \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_],
  )
]

// ==================== PAGE 2: SCHEDULE A ====================
#pagebreak()

#grid(
  columns: (0.85in, 1fr, 2.3in),
  column-gutter: 10pt,
  align: (left + horizon, left + horizon, right + horizon),
  image("images/logo.png", width: 0.8in),
  [
    #text(size: 13.5pt, weight: "bold", fill: pc-dark)[SCHEDULE A — CARD INTAKE & CONDITION LOG] \
    #v(2pt)
    #text(size: 8.5pt, fill: pc-green, weight: "semibold")[Attached to Pocket Cash Local Consignment & Bailee Agreement]
  ],
  [
    #text(size: 8.5pt)[
      *Consignor:* \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ \
      #v(4pt)
      *Intake Date:* \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
    ]
  ]
)

#v(4pt)
#line(length: 100%, stroke: 1.2pt + pc-green)
#v(4pt)

#text(size: 8pt, fill: rgb("#333333"))[
  *Instructions:* List each consigned card below before meet-up. Check *one (1) Condition Category* per card (this logged condition governs Section 9 Safe Custody Valuation; ungraded cards are never valued at graded prices). Consignor sets the Starting Bid (*\$15.00 min*) for 7-Day Auctions (*15% commission on \$500+ slabs / 25% standard*) or Buy-It-Now Price (*\$75.00 min*) for 30-Day BIN (*35% commission*).
]

#v(5pt)

#let intake-row(n) = (
  align(center + horizon)[#text(weight: "bold")[#n]],
  [],
  align(center + horizon)[#text(size: 7.2pt)[☐ Slab (Grade/Cert) \ ☐ Raw NM #h(4pt) ☐ Raw LP-]],
  align(center + horizon)[#text(size: 7.2pt)[☐ Auction (15/25%) \ ☐ BIN (35%)]],
  align(left + horizon)[#text(size: 8pt)[\$]],
  align(left + horizon)[#text(size: 8pt)[\$]],
  [],
)

#table(
  columns: (0.30in, 1fr, 1.32in, 1.08in, 0.80in, 0.80in, 0.50in),
  inset: (x: 4.5pt, y: 5.0pt),
  stroke: 0.6pt + rgb("#999999"),
  fill: (x, y) => if y == 0 { pc-dark } else if calc.even(y) { rgb("#f7faf8") } else { white },
  table.header(
    align(center + horizon)[#text(fill: white, weight: "bold", size: 8pt)[\#]],
    align(left + horizon)[#text(fill: white, weight: "bold", size: 8pt)[Year • Brand/Set • Player • Card \# • Serial / Parallel / Slab Cert \#]],
    align(center + horizon)[#text(fill: white, weight: "bold", size: 8pt)[Logged Condition \ (Check One)]],
    align(center + horizon)[#text(fill: white, weight: "bold", size: 8pt)[Listing Type \ (Check One)]],
    align(center + horizon)[#text(fill: white, weight: "bold", size: 8pt)[Start Bid (\$15+) \ or BIN (\$75+)]],
    align(center + horizon)[#text(fill: white, weight: "bold", size: 8pt)[Free Relist \ New Start \$]],
    align(center + horizon)[#text(fill: white, weight: "bold", size: 8pt)[Initials]],
  ),
  ..range(1, 16).map(n => intake-row(n)).flatten()
)

#v(8pt)

#block(
  width: 100%,
  fill: pc-light,
  stroke: 0.8pt + pc-border,
  radius: 4pt,
  inset: 8pt,
)[
  #grid(
    columns: (1fr, 1fr),
    column-gutter: 14pt,
    row-gutter: 8pt,
    [
      #text(size: 8.5pt, weight: "bold", fill: pc-dark)[INTAKE RECEIPT & CONDITION ACKNOWLEDGMENT] \
      #v(2pt)
      #text(size: 7.8pt)[
        Consignor confirms that the cards, logged conditions, and starting prices above are accurate, and that the non-refundable \$5.00/card Listing Fee has been paid.
      ] \
      #v(6pt)
      *Consignor Signature:* \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ *Date:* \_\_\_\_\_\_\_\_
    ],
    [
      #text(size: 8.5pt, weight: "bold", fill: pc-dark)[UNSOLD CARD RETURN RECEIPT (Complete Only If Returned)] \
      #v(2pt)
      #text(size: 7.8pt)[
        Consignor acknowledges return and receipt of unsold card line item(s) \#\_\_\_\_\_\_\_\_\_\_\_\_\_ in the same condition as logged at intake.
      ] \
      #v(6pt)
      *Return Signature:* \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ *Date:* \_\_\_\_\_\_\_\_
    ]
  )
]
