function initSkillGapRoadmap() {
    const triggers = document.querySelectorAll(".skill-roadmap-trigger");
    if (!triggers.length) {
        return;
    }

    let activeCard = null;

    triggers.forEach((trigger) => {
        const panel = trigger.nextElementSibling;
        if (!panel) {
            return;
        }

        if (trigger.getAttribute("aria-expanded") === "true") {
            activeCard = trigger;
        }

        trigger.addEventListener("click", () => {
            const isExpanded = trigger.getAttribute("aria-expanded") === "true";

            if (activeCard && activeCard !== trigger) {
                const prevPanel = activeCard.nextElementSibling;
                if (prevPanel) {
                    activeCard.setAttribute("aria-expanded", "false");
                    activeCard.classList.remove("is-active");
                    prevPanel.classList.remove("is-open");
                    prevPanel.setAttribute("aria-hidden", "true");
                }
            }

            if (isExpanded) {
                trigger.setAttribute("aria-expanded", "false");
                trigger.classList.remove("is-active");
                panel.classList.remove("is-open");
                panel.setAttribute("aria-hidden", "true");
                activeCard = null;
            } else {
                trigger.setAttribute("aria-expanded", "true");
                trigger.classList.add("is-active");
                panel.classList.add("is-open");
                panel.setAttribute("aria-hidden", "false");
                activeCard = trigger;
            }
        });
    });
}
