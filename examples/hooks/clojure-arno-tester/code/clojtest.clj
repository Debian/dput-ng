; Copyright (c) Paul R. Tagliamonte <paultag@debian.org>, 2012, under the
; terms of dput-ng it's self.

(ns clojtest
  (:require dput.core
            dput.exceptions))


(defn log [x]  ; for debug output
  (.debug dput.core/logger x))


(defn dput-checker [changes profile interface]
  (cond (>= (-> changes (.get "maintainer") (.find "arno@debian.org")) 0)
    (throw (dput.exceptions/HookException. "Maintainer's Arno. Aborting upload"))
  :else
    (log "Nah, it's not arno, we're good")))
