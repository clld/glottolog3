<%inherit file="home_comp.mako"/>

<h3>Contact ${h.contactmail(req, None, title='report a problem')}</h3>
    <div class="well">
        <p>You can contact us via email at <a href="mailto:glottolog@eva.mpg.de">glottolog@eva.mpg.de.</a>
        We are happy to receive additional bibliographies in any format, and feedback of any sort.</p>
        <p><a href="https://github.com">GitHub</a> users can also create and discuss bug reports using the following <strong>issue trackers</strong>:
        <ul>
            <li><a href="https://github.com/clld/glottolog-data/issues">clld/glottolog-data/issues</a> for errata on languoids &amp; references</li>
            <li><a href="https://github.com/clld/glottolog3/issues">clld/glottolog3/issues</a> for problems with the site software</li>
        </ul>
    </div>
