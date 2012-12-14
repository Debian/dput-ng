; Copyright (c) Gergely Nagy <algernon@debian.org>, 2012, under the
; terms of dput-ng itself.

(ns bd-blacklist
  (:require dput.core
            dput.exceptions
            dput.dsc))

(defn prune-build-deps
  "Prune a string representation of the build-depends so that only a
  list of packages remain."
  [bd-string]

  (map #(first (-> % (.strip) (.split " "))) (.. bd-string (split ","))))

(defn has-blacklisted?
  "Given a dsc file and a blacklist, check if any of the
  build-depencencies are in that list. Throws an error if there are
  matches."

  [dsc-file blacklist]

  (let [dsc (dput.dsc/parse_dsc_file dsc-file)
        build-deps (prune-build-deps (.. dsc (get "build-depends")))]
    (if-let [bad-bd (some blacklist build-deps)]
      (throw (dput.exceptions/HookException. (str "Blacklisted build-dependency found: " bad-bd)))
      (-> dput.core/logger (.trace "Build-Dependencies do not have anything on the blacklist")))))

(defn blacklist-checker
  "Checks whether the dsc has blacklisted build-dependencies, ignores
  the check when no dsc is to be found."

  [changes profile interface]

  (if-let [dsc-file (.. changes (get_dsc))]
    (has-blacklisted? dsc-file (set (get profile "bd-blacklist")))
    (-> dput.core/logger (.trace "No .dsc found, build-dependencies cannot be checked"))))
