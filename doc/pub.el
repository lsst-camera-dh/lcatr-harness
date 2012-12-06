(require 'org-publish)
(let ((default-directory "~/work/lsst/lcatr/harness/doc"))
)
(setq org-publish-project-alist
      
      `(                               ; personal wiki jumble of stuff
        ("html"               
         :base-extension "org"
         :base-directory , "."
         :publishing-directory , "html"
         :recursive t
         :publishing-function org-publish-org-to-html
         :headline-levels 3
         :auto-preamble t
         :auto-sitemap nil
         :sitemap-filename "sitemap.org"
         :sitemap-title "Sitemap"       

         )

        ("pdfs"               
         :base-extension "org"
         :base-directory , "."
         :publishing-directory , "pdf"
         :recursive t
         :publishing-function org-publish-org-to-pdf
         :headline-levels 3
         :auto-preamble t
         :auto-sitemap nil              
         :sitemap-filename "sitemap.org"
         :sitemap-title "Sitemap"       

         )
        
        ("all" :components ("html" "pdfs"))
        
        ))
(setq org-link-abbrev-alist
      '(
        ; link to ROOT's class docs
        ("tclass" . "http://root.cern.ch/root/html/%s")
        ))
