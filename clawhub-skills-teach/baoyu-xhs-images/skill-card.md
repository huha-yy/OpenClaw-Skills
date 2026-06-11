## Description: <br>
Generates infographic image card series with 12 visual styles, 8 layouts, and 3 color palettes, breaking content into 1-10 cartoon-style cards optimized for social media engagement. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[jimliu](https://clawhub.ai/user/jimliu) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
External creators and developers use this skill to turn source material into Xiaohongshu or WeChat-style infographic image-card series with selectable visual styles, layouts, palettes, confirmation steps, and reproducible prompt files. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The security review flags instructions that try to avoid refusals for sensitive or copyrighted figures. <br>
Mitigation: Apply the runtime platform's safety policy first; use stylized alternatives only when allowed and avoid generating prohibited public-figure, sensitive-person, or copyrighted-character content. <br>
Risk: The skill may create local prompt, preference, source, and image files during normal use. <br>
Mitigation: Use project-local preferences unless cross-project defaults are intended, and review generated files before sharing or publishing. <br>
Risk: The workflow depends on external or runtime image-generation backends selected at execution time. <br>
Mitigation: Confirm the selected backend before generation and review backend terms, privacy handling, and output safety before use. <br>


## Reference(s): <br>
- [ClawHub Skill Page](https://clawhub.ai/jimliu/baoyu-xhs-images) <br>
- [Project Homepage](https://github.com/JimLiu/baoyu-skills#baoyu-xhs-images) <br>
- [Confirmation Questions](references/confirmation.md) <br>
- [Style Presets](references/style-presets.md) <br>
- [Prompt Assembly Guide](references/workflows/prompt-assembly.md) <br>
- [Content Analysis Framework](references/workflows/analysis-framework.md) <br>
- [Preferences Schema](references/config/preferences-schema.md) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Markdown, Configuration, Guidance] <br>
**Output Format:** [Markdown guidance with saved prompt files and image-generation instructions] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Produces analysis, outlines, per-card prompts, and instructions for raster image generation through an available backend.] <br>

## Skill Version(s): <br>
2.0.0 (source: frontmatter and server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
